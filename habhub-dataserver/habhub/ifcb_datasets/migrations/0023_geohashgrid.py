# Generated by Django 3.1.14 on 2023-02-17 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifcb_datasets', '0022_auto_20230213_1818'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeohashGrid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geohash_token', models.CharField(db_index=True, max_length=100)),
                ('s2_grid_level', models.PositiveIntegerField()),
                ('region', models.CharField(choices=[('NE Atlantic', 'NE Atlantic'), ('SE Atlantic', 'SE Atlantic'), ('Pacific Coast', 'Pacific Coast'), ('Alaska', 'Alaska')], max_length=20)),
            ],
        ),
    ]
