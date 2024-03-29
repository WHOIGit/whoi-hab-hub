# Generated by Django 3.0.10 on 2021-01-03 13:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0020_auto_20201230_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datapoint',
            name='measurement_date',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='station',
            name='state',
            field=models.CharField(blank=True, choices=[('ME', 'Maine'), ('MA', 'Massachusetts'), ('NH', 'New Hampshire')], db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='station',
            name='station_location',
            field=models.CharField(db_index=True, max_length=100),
        ),
    ]
