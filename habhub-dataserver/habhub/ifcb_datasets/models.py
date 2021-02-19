from statistics import mean
from django.contrib.gis.db import models
from django.db.models import F
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.postgres.search import SearchVector
from django.utils import timezone

# IFCB dataset models

class Dataset(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=False, blank=True)
    geom =  models.PointField(srid=4326, null=True, blank=True)
    # the lookup name from the IFCB dashboard
    dashboard_id_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return F'{self.name} - {self.location}'

    def get_max_mean_values(self):
        TARGET_SPECIES = [species[0] for species in Bin.TARGET_SPECIES]
        # set up data structure to store results
        concentration_values = []
        max_mean_values = []

        for species in TARGET_SPECIES:
            concentration_dict = {'species': species, 'values': []}
            concentration_values.append(concentration_dict)

        bins_qs = self.bins.all()
        if bins_qs:
            for bin in bins_qs:
                for datapoint in bin.cell_concentration_data:
                    item = next((item for item in concentration_values if item['species'] == datapoint['species']), None)

                    if item is not None:
                        item['values'].append(int(datapoint['cell_concentration']))

            for item in concentration_values:
                data_dict = {
                    'species': item['species'],
                    'max_value': max(item['values']),
                    'mean_value': mean(item['values']),
                }
                max_mean_values.append(data_dict)

        return max_mean_values


class Bin(models.Model):
    ALEXANDRIUM_CATENELLA = 'Alexandrium_catenella'
    DINOPHYSIS_ACUMINATA = 'Dinophysis_acuminata'
    DINOPHYSIS_NORVEGICA = 'Dinophysis_norvegica'
    KARENIA = 'Karenia'
    MARGALEFIDINIUM = 'Margalefidinium'
    PSEUDO_NITZSCHIA = 'Pseudo-nitzschia'
    TARGET_SPECIES = (
        (ALEXANDRIUM_CATENELLA, 'Alexandrium catenella'),
        (DINOPHYSIS_ACUMINATA, 'Dinophysis acuminata'),
        (DINOPHYSIS_NORVEGICA, 'Dinophysis norvegica'),
        (KARENIA, 'Karenia'),
        (MARGALEFIDINIUM, 'Margalefidinium polykrikoides'),
        (PSEUDO_NITZSCHIA, 'Pseudo nitzschia'),
    )

    # the primary ID from the IFCB dashboard
    pid = models.CharField(max_length=100, unique=True, db_index=True)
    geom =  models.PointField(srid=4326, null=True, blank=True)
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
