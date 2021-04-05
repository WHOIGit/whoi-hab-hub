from django.db import models


class TargetSpecies(models.Model):
    # Model to configure Target HAB species for HABhub to monitor
    # Used for all data layers

    # species_id needs to match the Autoclass files in the IFCB Dashboard
    species_id = models.CharField(max_length=100, unique=True, db_index=True,
                                  help_text='Needs to match the species ID used in the Autoclass files from the IFCB Dashboard')
    display_name = models.CharField(max_length=100, blank=True, db_index=True)

    class Meta:
        ordering = ['species_id']
        verbose_name_plural = 'Target Species'

    def __str__(self):
        return self.display_name


class DataLayer(models.Model):
    # Model to configure which Data Layers are active for the frontend client
    layer_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=100, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
