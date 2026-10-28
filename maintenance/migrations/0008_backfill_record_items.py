from django.db import migrations

# Every record imported before component tracking existed was a fuel filter
# replacement of both the upper and lower filter, so analytics stay unchanged.
LEGACY_COMPONENTS = ['FILTER_SOLAR_ATAS', 'FILTER_SOLAR_BAWAH']


def backfill(apps, schema_editor):
    ComponentType = apps.get_model('master', 'ComponentType')
    Record = apps.get_model('maintenance', 'Record')
    RecordItem = apps.get_model('maintenance', 'RecordItem')

    # existing rows: take the component from their part
    for item in RecordItem.objects.filter(component_type__isnull=True).select_related('part'):
        item.component_type_id = item.part.component_type_id
        item.save(update_fields=['component_type'])

    for code in LEGACY_COMPONENTS:
        component = ComponentType.objects.get(code=code)
        covered = RecordItem.objects.filter(component_type=component).values('record_id')
        missing = Record.objects.exclude(pk__in=covered).values_list('pk', flat=True)
        RecordItem.objects.bulk_create(
            [RecordItem(record_id=pk, component_type=component, action='replace', quantity=1) for pk in missing.iterator()],
            batch_size=1000,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0007_recorditem'),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
