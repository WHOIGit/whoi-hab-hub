# Generated by Django 2.2.4 on 2019-09-16 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('closures', '0020_auto_20190916_1641'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='closurenotice',
            name='organism',
        ),
    ]
