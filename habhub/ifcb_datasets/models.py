from django.contrib.gis.db import models
from django.utils import timezone

# IFCB dataset models

class Dataset(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=False, blank=True)
    geom =  models.PointField(srid=4326, null=True, blank=True)
    dashboard_id_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return F'{self.name} - {self.location}'


class Bin(models.Model):
    pid = models.CharField(max_length=100, unique=True)
    geom =  models.PointField(srid=4326, null=True, blank=True)
    dataset = models.ForeignKey(Dataset, related_name='bins', on_delete=models.CASCADE)
    sample_time = models.DateTimeField(default=timezone.now)
    ifcb = models.IntegerField(null=True, blank=True)
    ml_analyzed = models.DecimalField(max_digits=15, decimal_places=14, null=True, blank=True)
    depth = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    cruise = models.CharField(max_length=50, null=False, blank=True)
    cast = models.CharField(max_length=50, null=False, blank=True)
    niskin = models.CharField(max_length=50, null=False, blank=True)
    sample_type = models.CharField(max_length=50, null=False, blank=True)
    n_images = models.IntegerField(null=True, blank=True)
    skip = models.BooleanField(default=False)

    class Meta:
        ordering = ['sample_time']

    def __str__(self):
        return self.pid
