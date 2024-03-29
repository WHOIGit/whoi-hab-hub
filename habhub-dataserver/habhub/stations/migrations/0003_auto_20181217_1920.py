# Generated by Django 2.0.9 on 2018-12-17 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0002_station_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='station',
            name='latitude',
            field=models.DecimalField(decimal_places=7, max_digits=10),
        ),
        migrations.AlterField(
            model_name='station',
            name='longitude',
            field=models.DecimalField(decimal_places=7, max_digits=10),
        ),
    ]
