# Generated by Django 2.2.4 on 2019-09-06 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('closures', '0015_auto_20190906_1351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='closurenotice',
            name='notice_action',
            field=models.CharField(choices=[('Open', 'Open'), ('Closed', 'Closed')], default='Open', max_length=50),
        ),
    ]
