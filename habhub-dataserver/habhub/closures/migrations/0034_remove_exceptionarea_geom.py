# Generated by Django 2.2.6 on 2019-11-18 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('closures', '0033_auto_20191118_1637'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exceptionarea',
            name='geom',
        ),
    ]
