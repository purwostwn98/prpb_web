from django.db import migrations

# The two fuel filter positions that existed as Part.jenis_part choices.
# 10.000 KM matches the "ideal" interval already used by the maintenance dashboard.
COMPONENT_TYPES = [
    ('FILTER_SOLAR_ATAS', 'Filter Solar Atas', 'filter_solar_atas'),
    ('FILTER_SOLAR_BAWAH', 'Filter Solar Bawah', 'filter_solar_bawah'),
]


def seed(apps, schema_editor):
    ComponentType = apps.get_model('master', 'ComponentType')
    Part = apps.get_model('master', 'Part')
    for code, name, jenis_part in COMPONENT_TYPES:
        component, _ = ComponentType.objects.get_or_create(
            code=code,
            defaults={'name': name, 'category': 'filter_solar', 'unit': 'pcs', 'interval_km': 10000},
        )
        Part.objects.filter(jenis_part=jenis_part).update(component_type=component)
    # parts with an unknown jenis_part fall back to the upper fuel filter
    Part.objects.filter(component_type__isnull=True).update(
        component_type=ComponentType.objects.get(code='FILTER_SOLAR_ATAS')
    )


def unseed(apps, schema_editor):
    Part = apps.get_model('master', 'Part')
    for code, _, jenis_part in COMPONENT_TYPES:
        Part.objects.filter(component_type__code=code).update(jenis_part=jenis_part)


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0011_componenttype_part_component_type'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
