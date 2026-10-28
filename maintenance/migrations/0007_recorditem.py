import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0013_part_component_type_required'),
        ('maintenance', '0006_truckdevicemodel'),
    ]

    operations = [
        migrations.RenameModel(old_name='RecordParts', new_name='RecordItem'),
        migrations.AlterField(
            model_name='recorditem',
            name='record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='maintenance.record'),
        ),
        migrations.AlterField(
            model_name='recorditem',
            name='part',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='master.part'),
        ),
        migrations.AlterField(
            model_name='recorditem',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
        ),
        migrations.AddField(
            model_name='recorditem',
            name='component_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='record_items', to='master.componenttype'),
        ),
        migrations.AddField(
            model_name='recorditem',
            name='action',
            field=models.CharField(choices=[('replace', 'Ganti'), ('top_up', 'Tambah / Top Up'), ('inspect', 'Inspeksi'), ('repair', 'Perbaikan')], default='replace', max_length=20),
        ),
        migrations.AddField(
            model_name='recorditem',
            name='unit_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name='recorditem',
            name='notes',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
