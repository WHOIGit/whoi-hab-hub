import datetime

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# ESP Models

class EspInstrument(models.Model):
    esp_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['esp_name']

    def __str__(self):
        return self.esp_name


class Deployment(models.Model):
    espinstrument = models.ForeignKey(EspInstrument, related_name='deployment',
                                on_delete=models.CASCADE, null=False)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    mooring_name = models.CharField(max_length=100)
    year = models.IntegerField(validators=[MinValueValidator(1984), MaxValueValidator(datetime.date.today().year)])

    class Meta:
        ordering = ['year']

    def __str__(self):
        return '%s - %s - %s' % (self.year, self.espinstrument.esp_name, self.mooring_name)
