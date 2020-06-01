from django.utils.timezone import now
from django.contrib.gis.db import models
from django.db.models import Avg, Max

# Create your models here.

class Station(models.Model):
    STATES = (
        ('ME', 'Maine'),
        ('MA', 'Massachusetts'),
        ('NH', 'New Hampshire'),
    )

    station_name = models.CharField(max_length=100)
    station_location = models.CharField(max_length=100)
    geom =  models.PointField(srid=4326, null=True, blank=True)
    state = models.CharField(max_length=50, choices=STATES, null=False, blank=True)

    class Meta:
        ordering = ['state', 'station_name']

    def __str__(self):
        return '%s - %s' % (self.station_name, self.station_location)

    def get_max_mean_values(self):
        return self.datapoints.aggregate(station_mean=Avg('measurement'), station_max=Max('measurement'))


class Species(models.Model):
    species_name = models.CharField(max_length=100)
    italicize = models.BooleanField(blank=False, default=False)

    def __str__(self):
        return self.species_name


class Datapoint(models.Model):
    station = models.ForeignKey(Station, related_name='datapoints',
                                on_delete=models.CASCADE, null=False)
    measurement = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    measurement_date = models.DateTimeField(default=now, null=False)
    species = models.ForeignKey(Species, related_name='datapoints',
                                on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['-measurement_date']
        get_latest_by = 'measurement_date'

    def __str__(self):
        return '%s - %s' % (self.station.station_name, self.measurement_date)
