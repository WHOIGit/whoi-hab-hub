# Generated by Django 2.2.8 on 2020-01-06 16:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esp_instrument', '0004_auto_20190117_1852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deployment',
            name='year',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1984), django.core.validators.MaxValueValidator(2020)]),
        ),
    ]
