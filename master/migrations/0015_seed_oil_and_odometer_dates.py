import datetime

from django.db import migrations
from django.db.models import Max
from django.utils import timezone


def forwards(apps, schema_editor):
    ComponentType = apps.get_model('master', 'ComponentType')
    Truck = apps.get_model('master', 'Truck')
    Record = apps.get_model('maintenance', 'Record')

    ComponentType.objects.get_or_create(
        code='OLI_MESIN',
        defaults={
            'name': 'Oli Mesin', 'category': 'oli', 'unit': 'liter',
            'interval_km': 10000, 'warning_km': 2000, 'track_reliability': True,
        },
    )

    # the stored odometer came from the latest maintenance record; date it accordingly
    for truck in Truck.objects.filter(odometer_updated_at__isnull=True):
        last_date = (
            Record.objects.filter(truck_id=truck.pk, odometer_reading=truck.current_odometer)
            .aggregate(d=Max('service_date'))['d']
        )
        if last_date:
            truck.odometer_updated_at = timezone.make_aware(datetime.datetime.combine(last_date, datetime.time(12)))
            truck.odometer_source = 'maintenance'
            truck.save(update_fields=['odometer_updated_at', 'odometer_source'])


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0014_odometer_and_warning_fields'),
        ('maintenance', '0009_recorditem_component_type_required'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
