# Generated by Django 2.2.4 on 2019-09-27 17:11

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('closures', '0025_auto_20190927_1423'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExceptionArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, null=True, srid=4326)),
                ('description', models.TextField(blank=True)),
                ('closure_notice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exception_areas', to='closures.ClosureNotice')),
                ('species', models.ManyToManyField(related_name='exception_areas', to='closures.Species')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
    ]