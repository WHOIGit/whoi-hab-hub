# Generated by Django 2.2.8 on 2020-03-03 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0011_auto_20200302_1431'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datapoint',
            old_name='measurement',
            new_name='measurement_old',
        ),
    ]