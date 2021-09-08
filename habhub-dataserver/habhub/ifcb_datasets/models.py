import datetime
from statistics import mean

from django.contrib.gis.db import models
from django.db.models import F
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.postgres.search import SearchVector
from django.utils import timezone

from habhub.core.models import TargetSpecies, DataLayer, Metric
from habhub.core.constants import IFCB_LAYER
from .api_requests import _get_ifcb_autoclass_file
# IFCB dataset models


class Dataset(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=False, blank=True)
    geom = models.PointField(srid=4326, null=True, blank=True)
    # the lookup name from the IFCB dashboard
    dashboard_id_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return F'{self.name} - {self.location}'

    def get_data_layer_metrics(self):
        metrics = Metric.objects.filter(data_layer__belongs_to_app=DataLayer.IFCB_DATASETS)
        return metrics

    def get_max_mean_values(self):
        target_list = TargetSpecies.objects.values_list('species_id', flat=True)
        metrics = self.get_data_layer_metrics()
        for metric in metrics:
            print(metric)

        # set up data structure to store results
        data_values = []
        max_mean_values = []

        for species in target_list:
            concentration_dict = {
                'species': species,
                'metrics': [{'metric_id': metric.metric_id, 'name': metric.name, 'units': metric.units,'values': []} for metric in metrics]
            }
            data_values.append(concentration_dict)

        if self.bins.exists():
            bins_qs = self.bins.all()
            for bin in bins_qs:
                if bin.cell_concentration_data:
                    for datapoint in bin.cell_concentration_data:
                        item = next(
                            (item for item in data_values if item['species'] == datapoint['species']), None)

                        if item:
                            for metric in metrics:
                                metric_item = next(
                                    (metric_item for metric_item in item['metrics'] if metric_item['metric_id'] == metric.metric_id), None
                                )

                                try:
                                    metric_item['values'].append(int(datapoint[metric.metric_id]))
                                except:
                                    pass

            for item in data_values:
                print(item)
                data_list = []

                #biovolumes = {'metric_name': 'Biovolume', 'max_value': 0, 'mean_value': 0, 'units': 'cubic microns/L'}

                for metric_item in item['metrics']:
                    metric_data = {'metric_name': metric_item['name'], 'max_value': 0, 'mean_value': 0, 'units': metric_item['units']}
                    if metric_item['values']:
                        metric_data['max_value'] = max(metric_item['values'])
                        metric_data['mean_value'] = mean(metric_item['values'])

                    data_list.append(metric_data)
                #data_list.append(biovolumes)
                data_dict = {
                    'species': item['species'],
                    'data': data_list
                }
                max_mean_values.append(data_dict)

        return max_mean_values

    def ingest_ifcb_data_range(self, start_date, end_date):
        if start_date:
            start_date_obj = datetime.datetime.strptime(start_date, "%m/%d/%Y").date()
        else:
            return "Start Date missing"

        if end_date:
            end_date_obj = datetime.datetime.strptime(end_date, "%m/%d/%Y").date()
        else:
            end_date_obj = timezone.now()


        bins_qs = self.bins.filter(sample_time__range=(start_date_obj, end_date_obj))
        for bin in bins_qs:
            _get_ifcb_autoclass_file(bin)

        return "IFCB Bin date range ingested"


class Bin(models.Model):
    # the primary ID from the IFCB dashboard
    pid = models.CharField(max_length=100, unique=True, db_index=True)
    geom = models.PointField(srid=4326, null=True, blank=True)
    dataset = models.ForeignKey(Dataset, related_name='bins', on_delete=models.CASCADE)
    sample_time = models.DateTimeField(default=timezone.now, db_index=True)
    ifcb = models.PositiveIntegerField(null=True, blank=True)
    ml_analyzed = models.DecimalField(max_digits=17, decimal_places=14, null=True, blank=True)
    depth = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    cruise = models.CharField(max_length=50, null=False, blank=True)
    cast = models.CharField(max_length=50, null=False, blank=True)
    niskin = models.CharField(max_length=50, null=False, blank=True)
    sample_type = models.CharField(max_length=50, null=False, blank=True)
    n_images = models.PositiveIntegerField(null=True, blank=True)
    skip = models.BooleanField(default=False)
    species_found = ArrayField(models.CharField(max_length=500), null=True, blank=True, default=None)
    # Units are cells/L : cell_concentration = (image_numbers / bin.ml_analyzed) * 1000
    cell_concentration_data = JSONField(null=True)

    class Meta:
        ordering = ['-sample_time']
        get_latest_by = 'sample_time'

    def __str__(self):
        return self.pid

    def get_concentration_units(self):
        return 'cells/L'

    def get_concentration_data_by_species(self, species):
        if self.cell_concentration_data:
            item = next((item for item in self.cell_concentration_data if item['species'] == species), False)
            return item
        return None
