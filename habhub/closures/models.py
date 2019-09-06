import datetime

from django.db import models
from django.utils import timezone
from djgeojson.fields import PointField, PolygonField

# Create your models here.

class ClosureArea(models.Model):
    STATES = (
        ('ME', 'Maine'),
        ('MA', 'Massachusetts'),
        ('NH', 'New Hampshire'),
    )

    CURRENT_STATUS = (
        ('Open', 'Open'),
        ('Closed', 'Closed'),
    )

    name = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=50, choices=STATES, null=False, blank=True, db_index=True)
    geom = PolygonField()
    acres = models.DecimalField(max_digits=19, decimal_places=10, null=True)
    area_description = models.CharField(max_length=1000, null=False, blank=True)
    area_class = models.CharField(max_length=100, null=False, blank=True)
    current_status = models.CharField(max_length=100, choices=CURRENT_STATUS, null=False, blank=True, default='Open', db_index=True)

    class Meta:
        ordering = ['state', 'name']

    def __str__(self):
        return self.name


class Species(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Species'

    def __str__(self):
        return self.name


class ClosureNotice(models.Model):
    NOTICE_ACTION = (
        ('Open', 'Open'),
        ('Closed', 'Closed'),
    )

    SYNDROME = (
        ('PSP', 'Paralytic Shellfish Poison (PSP)'),
        ('DSP', 'Diarrhetic shellfish poisoning (DSP)'),
        ('ASP', 'Amnesic shellfish poisoning (ASP)'),
    )

    ORGANISMS = (
        ('Alexandrium spp.', 'Alexandrium spp.'),
        ('Dinophysis sp.', 'Dinophysis sp.'),
    )

    title = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    closure_areas = models.ManyToManyField(ClosureArea, related_name='closure_notices')
    species = models.ManyToManyField(Species, related_name='closure_notices')
    notice_action = models.CharField(max_length=50, choices=NOTICE_ACTION, default='Open')
    syndrome = models.CharField(max_length=50, choices=SYNDROME, null=False, blank=True, default='PSP')
    causative_organism = models.CharField(max_length=50, choices=ORGANISMS, null=False, blank=True)
    document = models.FileField(upload_to='closure_notices/', null=True, blank=True)
    comments = models.TextField(null=False, blank=True)

    class Meta:
        ordering = ['date', 'title']

    def __str__(self):
        return self.title
