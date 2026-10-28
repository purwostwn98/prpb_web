import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0010_alter_spbu_created_at_alter_spbu_updated_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComponentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Kode unik, mis. OLI_MESIN', max_length=50, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('category', models.CharField(choices=[('filter_solar', 'Filter Solar'), ('filter', 'Filter Lainnya'), ('oli', 'Oli / Pelumas'), ('ban', 'Ban'), ('rem', 'Rem'), ('kelistrikan', 'Kelistrikan / Aki'), ('lainnya', 'Lainnya')], max_length=30)),
                ('unit', models.CharField(choices=[('pcs', 'Pcs'), ('liter', 'Liter'), ('set', 'Set')], default='pcs', max_length=10)),
                ('interval_km', models.PositiveIntegerField(blank=True, help_text='Interval penggantian (KM)', null=True)),
                ('interval_days', models.PositiveIntegerField(blank=True, help_text='Interval penggantian (hari)', null=True)),
                ('track_reliability', models.BooleanField(default=True, help_text='Ikut dihitung MTTF / reliability')),
                ('is_active', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='part',
            name='component_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='parts', to='master.componenttype'),
        ),
    ]
