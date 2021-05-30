import s2sphere
from statistics import mean
from django.contrib.gis.db import models
from django.db.models import F
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.postgres.search import SearchVector
from django.utils import timezone

from habhub.core.models import TargetSpecies
from .managers import DatasetQuerySet

# IFCB dataset models


class Dataset(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=False, blank=True)
    geom = models.PointField(srid=4326, null=True, blank=True)
    # the lookup name from the IFCB dashboard
    dashboard_id_name = models.CharField(max_length=100)
    fixed_location = models.BooleanField(default=True)

    #objects = DatasetQuerySet.as_manager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return F'{self.name} - {self.location}'

    def get_max_mean_values(self):
        target_list = TargetSpecies.objects.values_list('species_id', flat=True)
        # set up data structure to store results
        concentration_values = []
        max_mean_values = []

        for species in target_list:
            concentration_dict = {'species': species, 'values': []}
            concentration_values.append(concentration_dict)

        if self.bins.exists():
            bins_qs = self.bins.all()
            for bin in bins_qs:
                if bin.cell_concentration_data:
                    for datapoint in bin.cell_concentration_data:
                        item = next(
                            (item for item in concentration_values if item['species'] == datapoint['species']), None)

                        if item is not None:
                            item['values'].append(int(datapoint['cell_concentration']))

            for item in concentration_values:
                if item['values']:
                    max_value = max(item['values'])
                    mean_value = mean(item['values'])
                else:
                    max_value = 0
                    mean_value = 0

                data_dict = {
                    'species': item['species'],
                    'max_value': max_value,
                    'mean_value': mean_value,
                }
                max_mean_values.append(data_dict)

        return max_mean_values


class Bin(models.Model):
    # the primary ID from the IFCB dashboard
    pid = models.CharField(max_length=100, unique=True, db_index=True)
    geom = models.PointField(srid=4326, null=True, blank=True)
    geom_s2_token = models.CharField(max_length=100, db_index=True, null=True, blank=True)
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

    # Custom save method to add S2 token for each lat/lng Point
    def save(self, *args, **kwargs):
        # s2 cell level of ~1.27 km^2 to represent lat/lng of Bins
        cell_level = 13
        try:
            ll = s2sphere.LatLng.from_degrees(self.geom.coords[1], self.geom.coords[0])
            cellid = s2sphere.CellId.from_lat_lng(ll).parent(cell_level)
            token = cellid.to_token()
            self.geom_s2_token = token
        except Exception as e:
            pass
        super(Bin, self).save(*args, **kwargs)

    def get_concentration_units(self):
        return 'cells/L'

    def get_concentration_data_by_species(self, species):
        if self.cell_concentration_data:
            item = next((item for item in self.cell_concentration_data if item['species'] == species), False)
            return item
        return None
