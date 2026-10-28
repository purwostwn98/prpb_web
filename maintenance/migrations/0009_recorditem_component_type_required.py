import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0008_backfill_record_items'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recorditem',
            name='component_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='record_items', to='master.componenttype'),
        ),
    ]
