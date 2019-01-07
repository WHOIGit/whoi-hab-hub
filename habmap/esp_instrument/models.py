from django.db import models

# Create your models here.

class EspInstrument(models.Model):
    esp_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['esp_name']

    def __str__(self):
        return self.esp_name
