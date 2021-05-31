# Generated by Django 3.0.10 on 2021-05-30 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifcb_datasets', '0013_dataset_fixed_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='bin',
            name='geom_s2_hash',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True, unique=True),
        ),
    ]