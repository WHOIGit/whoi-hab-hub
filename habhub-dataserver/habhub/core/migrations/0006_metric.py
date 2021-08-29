# Generated by Django 3.0.10 on 2021-08-29 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20210819_1516'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metric_id', models.CharField(db_index=True, max_length=100)),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('units', models.CharField(blank=True, max_length=100)),
                ('data_layer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='core.DataLayer')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
