from django.db import models

# Create your models here.

class Station(models.Model):
    STATES = (
        ('Maine', 'Maine'),
        ('Massachusetts', 'Massachusetts'),
    )

    station_name = models.CharField(max_length=100)
    station_location = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    species = models.CharField(max_length=100)
    state = models.CharField(max_length=50, choices=STATES, null=False, blank=True)


    class MPTTMeta:
        order_insertion_by = ['weight', 'name']

    def __str__(self):
        return self.name
