# Generated by Django 2.2.6 on 2019-11-18 16:37

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('closures', '0032_landmark'),
    ]

    operations = [
        migrations.AlterField(
            model_name='landmark',
            name='coords',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]