from colour import Color

from django.db import models
from django.contrib.postgres.fields import ArrayField
from colorfield.fields import ColorField

from .utils import linear_gradient


class TargetSpecies(models.Model):
    # Model to configure Target HAB species for HABhub to monitor
    # Used for all data layers

    SALTWATER = 'Saltwater'
    FRESHWATER = 'Freshwater'
    ENVIRONMENT_CHOICES = [
        (SALTWATER, 'Saltwater'),
        (FRESHWATER, 'Freshwater'),
    ]

    # species_id needs to match the Autoclass files in the IFCB Dashboard
    species_id = models.CharField(max_length=100, unique=True, db_index=True,
                                  help_text='Needs to match the species ID used in the Autoclass files from the IFCB Dashboard')
    display_name = models.CharField(max_length=100, db_index=True)
    syndrome = models.CharField(max_length=100, blank=True)
    primary_color = ColorField(default='#FF0000')
    color_gradient = ArrayField(
        models.CharField(max_length=7), null=True, blank=True, default=None
    )
    species_environment = models.CharField(
        max_length=20,
        choices=ENVIRONMENT_CHOICES,
        default=SALTWATER,
    )

    class Meta:
        ordering = ['species_id']
        verbose_name_plural = 'Target Species'

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        # Custom save method to create color gradient based on primary_color
        dark_shade = Color(self.primary_color)
        dark_shade.luminance = .35
        color_gradient = linear_gradient(self.primary_color, "#FFFFFF", 5)
        # remove white
        color_gradient.pop()
        # add dark_shade
        color_gradient.insert(0, dark_shade.hex)
        color_gradient.reverse()
        self.color_gradient = color_gradient
        super(TargetSpecies, self).save(*args, **kwargs)


class DataLayer(models.Model):
    # Model to configure which Data Layers are active for the frontend client
    layer_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=100, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
