# Generated by Django 4.2.20 on 2025-05-09 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0003_part'),
    ]

    operations = [
        migrations.AlterField(
            model_name='part',
            name='vendor',
            field=models.ManyToManyField(related_name='parts', to='master.vendor'),
        ),
    ]
