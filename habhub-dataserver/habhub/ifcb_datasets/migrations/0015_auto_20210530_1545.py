# Generated by Django 3.0.10 on 2021-05-30 15:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ifcb_datasets', '0014_bin_geom_s2_hash'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bin',
            old_name='geom_s2_hash',
            new_name='geom_s2_token',
        ),
    ]
