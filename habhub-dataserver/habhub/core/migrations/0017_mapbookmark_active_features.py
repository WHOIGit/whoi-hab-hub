# Generated by Django 3.1.14 on 2023-02-28 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_mapbookmark_max_mean'),
    ]

    operations = [
        migrations.AddField(
            model_name='mapbookmark',
            name='active_features',
            field=models.JSONField(blank=True, null=True),
        ),
    ]