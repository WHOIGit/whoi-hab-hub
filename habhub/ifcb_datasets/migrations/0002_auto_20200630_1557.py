# Generated by Django 2.2.13 on 2020-06-30 19:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ifcb_datasets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bin',
            name='sample_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
