# Generated by Django 2.2.13 on 2020-07-18 18:05

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ifcb_datasets', '0003_auto_20200701_1604'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bin',
            options={'ordering': ['-sample_time']},
        ),
        migrations.AddField(
            model_name='bin',
            name='target_species_found',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='SpeciesClassified',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('species', models.CharField(max_length=100)),
                ('image_count', models.PositiveIntegerField(default=0)),
                ('cell_concentration', models.PositiveIntegerField(default=0)),
                ('image_numbers', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, size=None)),
                ('bin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='species_classified', to='ifcb_datasets.Bin')),
            ],
            options={
                'ordering': ['species'],
            },
        ),
    ]
