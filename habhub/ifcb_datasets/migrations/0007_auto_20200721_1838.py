# Generated by Django 2.2.13 on 2020-07-21 18:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ifcb_datasets', '0006_bin_cell_concentration_data'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bin',
            options={'get_latest_by': 'sample_time', 'ordering': ['-sample_time']},
        ),
    ]
