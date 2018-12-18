# Generated by Django 2.0.9 on 2018-12-18 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0007_auto_20181218_1936'),
    ]

    operations = [
        migrations.AddField(
            model_name='datapoint',
            name='species',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='datapoint', to='stations.Species'),
        ),
    ]
