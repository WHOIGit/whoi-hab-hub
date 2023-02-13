# Generated by Django 3.1.14 on 2023-02-13 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_targetspecies_species_type'),
        ('ifcb_datasets', '0020_aggregatedatasetmetric_aggregategeospatialmetric'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aggregatedatasetmetric',
            name='metrics',
        ),
        migrations.AddField(
            model_name='aggregatedatasetmetric',
            name='biovolume_max',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='aggregatedatasetmetric',
            name='biovolume_mean',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='aggregatedatasetmetric',
            name='cell_concentration_max',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='aggregatedatasetmetric',
            name='cell_concentration_mean',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='aggregatedatasetmetric',
            name='species',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aggregate_dataset_metrics', to='core.targetspecies'),
        ),
        migrations.AlterField(
            model_name='aggregatedatasetmetric',
            name='dataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aggregate_dataset_metrics', to='ifcb_datasets.dataset'),
        ),
    ]
