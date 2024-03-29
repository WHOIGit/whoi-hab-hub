# Generated by Django 2.2.8 on 2020-01-06 16:48

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring_systems', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitoringsystem',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='monitoringsystem',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='monitoringsystem',
            name='alt_location',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='monitoringsystem',
            name='alt_url',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='monitoringsystem',
            name='location',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='monitoringsystem',
            name='system_type',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('Monitoring', 'Monitoring'), ('Forecasting', 'Forecasting')], default='Monitoring', max_length=22),
        ),
        migrations.AlterField(
            model_name='monitoringsystem',
            name='url',
            field=models.URLField(blank=True),
        ),
    ]
