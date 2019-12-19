from django.contrib.gis.db import models

class MonitoringSystem(models.Model):
    SYSTEM_TYPES = (
        ('Monitoring', 'Monitoring'),
        ('Forecasting', 'Forecasting'),
    )

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=False, blank=True)
    geom =  models.PointField(srid=4326, null=True, blank=True)
    system_type = models.CharField(max_length=50, choices=SYSTEM_TYPES, null=False, blank=True, default='Monitoring')
    url = models.URLField(max_length=200)
    location = models.CharField(max_length=100)
    alt_url = models.URLField(max_length=200)
    alt_location = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
