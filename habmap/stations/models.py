from django.utils.timezone import now

from django.db import models

# Create your models here.

class Station(models.Model):
    STATES = (
        ('Maine', 'Maine'),
        ('Massachusetts', 'Massachusetts'),
    )

    station_name = models.CharField(max_length=100)
    station_location = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    species = models.CharField(max_length=100)
    state = models.CharField(max_length=50, choices=STATES, null=False, blank=True)

    class Meta:
        ordering = ['state', 'station_name']

    def __str__(self):
        return self.station_name


class Datapoint(models.Model):
    station = models.ForeignKey(Station, related_name='datapoint',
                                on_delete=models.CASCADE, null=False)
    measurement = models.CharField(max_length=20, null=False, blank=True)
    measurement_date = models.DateTimeField(default=now, null=False)

    def __str__(self):
        return '%s - %s' % (self.station.station_name, self.measurement_date)
