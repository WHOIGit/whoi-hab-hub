# Generated by Django 2.2.4 on 2019-09-06 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('closures', '0014_auto_20190906_1349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='closurenotice',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to='closure_notices/'),
        ),
    ]
