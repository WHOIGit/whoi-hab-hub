# Generated by Django 2.2.4 on 2019-08-27 16:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('closures', '0009_auto_20190827_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='closurenotice',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]