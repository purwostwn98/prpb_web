import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0012_seed_component_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='part',
            name='component_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parts', to='master.componenttype'),
        ),
        migrations.RemoveField(
            model_name='part',
            name='jenis_part',
        ),
    ]
