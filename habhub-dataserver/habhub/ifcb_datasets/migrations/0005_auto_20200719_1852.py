# Generated by Django 2.2.13 on 2020-07-19 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifcb_datasets', '0004_auto_20200718_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bin',
            name='ifcb',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='bin',
            name='n_images',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='speciesclassified',
            name='species',
            field=models.CharField(choices=[('Alexandrium_catenella', 'Alexandrium catenella'), ('Dinophysis', 'Dinophysis'), ('Dinophysis_acuminata', 'Dinophysis acuminata'), ('Dinophysis_norvegica', 'Dinophysis norvegica')], max_length=100),
        ),
    ]
