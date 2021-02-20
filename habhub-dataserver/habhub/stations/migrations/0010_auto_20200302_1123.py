# Generated by Django 2.2.8 on 2020-03-02 16:23

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0009_auto_20190107_2011'),
    ]

    operations = [
        migrations.AddField(
            model_name='station',
            name='geom',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='datapoint',
            name='species',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='datapoints', to='stations.Species'),
        ),
        migrations.AlterField(
            model_name='datapoint',
            name='station',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datapoints', to='stations.Station'),
        ),
        migrations.AlterField(
            model_name='station',
            name='state',
            field=models.CharField(blank=True, choices=[('ME', 'Maine'), ('MA', 'Massachusetts'), ('NH', 'New Hampshire')], max_length=50),
        ),
    ]