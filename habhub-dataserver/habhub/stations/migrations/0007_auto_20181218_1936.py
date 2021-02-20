# Generated by Django 2.0.9 on 2018-12-18 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0006_auto_20181218_1924'),
    ]

    operations = [
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('species_name', models.CharField(max_length=100)),
                ('italicize', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='station',
            name='species',
        ),
    ]