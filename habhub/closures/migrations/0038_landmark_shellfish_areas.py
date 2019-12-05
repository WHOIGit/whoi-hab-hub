# Generated by Django 2.2.6 on 2019-12-05 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('closures', '0037_closurenotice_data_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='landmark',
            name='shellfish_areas',
            field=models.ManyToManyField(related_name='landmarks', to='closures.ShellfishArea'),
        ),
    ]
