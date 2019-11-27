# Generated by Django 2.2.6 on 2019-11-27 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('closures', '0035_auto_20191118_2001'),
    ]

    operations = [
        migrations.RenameField(
            model_name='landmark',
            old_name='coords',
            new_name='geom',
        ),
        migrations.AlterField(
            model_name='closurenotice',
            name='border_east',
            field=models.ManyToManyField(blank=True, null=True, related_name='closure_notices_east', to='closures.Landmark'),
        ),
        migrations.AlterField(
            model_name='closurenotice',
            name='border_west',
            field=models.ManyToManyField(blank=True, null=True, related_name='closure_notices_west', to='closures.Landmark'),
        ),
    ]
