from django.utils.timezone import now
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import Avg, Max

from habhub.core import constants, fields
from .managers import StationQuerySet

# function to return a list for setting hab_species default
def get_hab_species_default():
    all_species_list = list(dict(constants.TARGET_SPECIES).keys())
    station_default = [species for species in all_species_list if species == 'Alexandrium_catenella']
    return station_default

class Station(models.Model):
    STATES = (
        ('ME', 'Maine'),
        ('MA', 'Massachusetts'),
        ('NH', 'New Hampshire'),
    )

    station_name = models.CharField(max_length=100, null=True, blank=True)
    station_location = models.CharField(max_length=100, db_index=True)
    geom =  models.PointField(srid=4326, null=True, blank=True)
    state = models.CharField(max_length=50, choices=STATES, null=False, blank=True, db_index=True)
    hab_species = fields.ChoiceArrayField(models.CharField(
        choices = constants.TARGET_SPECIES,
        max_length = 50,
    ), default = get_hab_species_default)

    objects = StationQuerySet.as_manager()

    class Meta:
        ordering = ['state', 'station_name']

    def __str__(self):
        return '%s - %s' % (self.station_name, self.station_location)

    def get_max_mean_values(self):
        max_mean_values = []
        agg_dict = self.datapoints.aggregate(station_mean=Avg('measurement'), station_max=Max('measurement'))

        if agg_dict['station_max'] and agg_dict['station_mean']:
            data_dict = {
                'species': 'Alexandrium_catenella',
                'max_value': float(round(agg_dict['station_max'], 1)),
                'mean_value': float(round(agg_dict['station_mean'], 1)),
            }
            max_mean_values.append(data_dict)
        return max_mean_values


class Datapoint(models.Model):
    station = models.ForeignKey(Station, related_name='datapoints',
                                on_delete=models.CASCADE, null=False)
    measurement = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    measurement_date = models.DateTimeField(default=now, null=False, db_index=True)
    species_tested = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ['-measurement_date']
        get_latest_by = 'measurement_date'

    def __str__(self):
        return self.measurement_date
