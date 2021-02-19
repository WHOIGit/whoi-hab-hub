from django.contrib.gis.db import models
from multiselectfield import MultiSelectField

class MonitoringSystem(models.Model):
    SYSTEM_TYPES = (
        ('Monitoring', 'Monitoring'),
        ('Forecasting', 'Forecasting'),
    )

    name = models.CharField(max_length=1000)
    description = models.CharField(max_length=1000, null=False, blank=True)
    geom =  models.PointField(srid=4326, null=True, blank=True)
    system_type = MultiSelectField(choices=SYSTEM_TYPES, null=False, blank=True, default='Monitoring', max_length=100)
    url = models.URLField(max_length=200, null=False, blank=True)
    location = models.CharField(max_length=100, null=False, blank=True)
    alt_url = models.URLField(max_length=200, null=False, blank=True)
    alt_location = models.CharField(max_length=100, null=False, blank=True)
    latitude = models.CharField(max_length=100, null=False, blank=True)
    longitude = models.CharField(max_length=100, null=False, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
