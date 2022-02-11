import datetime
from statistics import mean

from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils import timezone

from habhub.core.models import TargetSpecies, DataLayer, Metric
from habhub.ifcb_datasets.tasks import reset_ifcb_dataset_data
from .managers import BinQuerySet

# IFCB dataset models


class Dataset(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=False, blank=True)
    geom = models.PointField(srid=4326, null=True, blank=True)
    # the lookup name from the IFCB dashboard
    dashboard_id_name = models.CharField(max_length=100)
    fixed_location = models.BooleanField(default=True)

    # objects = DatasetQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.location}"

    def reset_bin_data(self):
        reset_ifcb_dataset_data.delay(self.id)
        return f"{self.name} data reset started"

    def get_data_layer_metrics(self):
        metrics = Metric.objects.filter(
            data_layers__belongs_to_app=DataLayer.IFCB_DATASETS
        ).distinct()
        return metrics

    def get_max_mean_values(self):
        target_list = TargetSpecies.objects.values_list("species_id", flat=True)
        metrics = self.get_data_layer_metrics()

        # set up data structure to store results
        data_values = []
        max_mean_values = []

        for species in target_list:
            concentration_dict = {
                "species": species,
                "metrics": [
                    {
                        "metric_id": metric.metric_id,
                        "name": metric.name,
                        "units": metric.units,
                        "values": [],
                    }
                    for metric in metrics
                ],
            }
            data_values.append(concentration_dict)

        if self.bins.exists():

            bins_qs = self.bins.all()

            for bin in bins_qs:
                if bin.cell_concentration_data:
                    for datapoint in bin.cell_concentration_data:
                        item = next(
                            (
                                item
                                for item in data_values
                                if item["species"] == datapoint["species"]
                            ),
                            None,
                        )

                        if item:
                            for metric in metrics:
                                metric_item = next(
                                    (
                                        metric_item
                                        for metric_item in item["metrics"]
                                        if metric_item["metric_id"] == metric.metric_id
                                    ),
                                    None,
                                )

                                try:
                                    metric_item["values"].append(
                                        int(datapoint[metric.metric_id])
                                    )
                                except Exception as e:
                                    pass

            for item in data_values:
                data_list = []

                for metric_item in item["metrics"]:
                    metric_data = {
                        "metric_id": metric_item["metric_id"],
                        "metric_name": metric_item["name"],
                        "max_value": 0,
                        "mean_value": 0,
                        "units": metric_item["units"],
                    }
                    if metric_item["values"]:
                        metric_data["max_value"] = max(metric_item["values"])
                        metric_data["mean_value"] = mean(metric_item["values"])

                    data_list.append(metric_data)
                # data_list.append(biovolumes)
                data_dict = {"species": item["species"], "data": data_list}
                max_mean_values.append(data_dict)

        return max_mean_values


class Bin(models.Model):
    # the primary ID from the IFCB dashboard
    pid = models.CharField(max_length=100, unique=True, db_index=True)
    geom = models.PointField(srid=4326, null=True, blank=True)
    geom_s2_token = models.CharField(
        max_length=100, db_index=True, null=True, blank=True
    )
    dataset = models.ForeignKey(Dataset, related_name="bins", on_delete=models.CASCADE)
    sample_time = models.DateTimeField(default=timezone.now, db_index=True)
    ifcb = models.PositiveIntegerField(null=True, blank=True)
    ml_analyzed = models.DecimalField(
        max_digits=17, decimal_places=14, null=True, blank=True
    )
    depth = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    cruise = models.CharField(max_length=50, null=False, blank=True)
    cast = models.CharField(max_length=50, null=False, blank=True)
    niskin = models.CharField(max_length=50, null=False, blank=True)
    sample_type = models.CharField(max_length=50, null=False, blank=True)
    n_images = models.PositiveIntegerField(null=True, blank=True)
    skip = models.BooleanField(default=False)
    species_found = ArrayField(
        models.CharField(max_length=500), null=True, blank=True, default=None
    )
    # cell_concentration: cells/L (image_numbers / bin.ml_analyzed) * 1000
    cell_concentration_data = JSONField(null=True)

    objects = BinQuerySet.as_manager()

    class Meta:
        ordering = ["-sample_time"]
        get_latest_by = "sample_time"

    def __str__(self):
        return self.pid

    def get_concentration_units(self):
        return "cells/L"

    def get_concentration_data_by_species(self, species):
        if self.cell_concentration_data:
            item = next(
                (
                    item
                    for item in self.cell_concentration_data
                    if item["species"] == species
                ),
                False,
            )
            return item
        return None


class AutoclassScore(models.Model):
    # the primary ID from the IFCB dashboard, also denotes the image file name
    pid = models.CharField(max_length=100, unique=True, db_index=True)
    score = models.DecimalField(max_digits=7, decimal_places=6)
    species = models.ForeignKey(
        TargetSpecies, related_name="autoclass_scores", on_delete=models.CASCADE
    )
    bin = models.ForeignKey(
        Bin, related_name="autoclass_scores", on_delete=models.CASCADE
    )
