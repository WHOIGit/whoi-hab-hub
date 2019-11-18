import datetime

from django.contrib.gis.db import models
from django.utils import timezone
from django.utils.html import format_html
from djgeojson.fields import PointField, PolygonField

# Closure app models.

class ShellfishArea(models.Model):
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
    geom =  models.MultiPolygonField(srid=4326)
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


class CausativeOrganism(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

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

    title = models.CharField(max_length=100)
    notice_date = models.DateField(default=timezone.now)
    effective_date = models.DateField(default=timezone.now)
    shellfish_areas = models.ManyToManyField(ShellfishArea, related_name='closure_notices')
    custom_borders =  models.MultiLineStringField(srid=4326, null=True, blank=True)
    custom_geom =  models.MultiPolygonField(srid=4326, null=True, blank=True)
    species = models.ManyToManyField(Species, related_name='closure_notices')
    notice_action = models.CharField(max_length=50, choices=NOTICE_ACTION, default='Open')
    syndrome = models.CharField(max_length=50, choices=SYNDROME, null=False, blank=True, default='PSP')
    causative_organism = models.ForeignKey(CausativeOrganism, related_name='closure_notices',
                                on_delete=models.SET_NULL, null=True, blank=True)
    document = models.FileField(upload_to='closure_notices/', null=True, blank=True)
    comments = models.TextField(null=False, blank=True)

    class Meta:
        ordering = ['notice_date', 'title']

    def __str__(self):
        return self.title

    def get_shellfish_areas(self):
        return ", ".join([str(area) for area in self.shellfish_areas.all()])
    get_shellfish_areas.short_description = 'Shellfish Areas'

    def get_state(self):
        area = self.shellfish_areas.first()
        state = area.get_state_display()
        return state
    get_state.short_description = 'State'


class ClosureNoticeMaine(ClosureNotice):
    class Meta:
        proxy = True
        verbose_name = 'Closure notice (Maine)'
        verbose_name_plural = 'Closure notices (Maine)'


class ExceptionArea(models.Model):
    title = models.CharField(max_length=100)
    species = models.ManyToManyField(Species, related_name='exception_areas')
    closure_notice = models.ForeignKey(ClosureNotice, related_name='exception_areas',
                                on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=False, blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class BaseAreaShape(models.Model):
    STATES = (
        ('ME', 'Maine'),
        ('MA', 'Massachusetts'),
        ('NH', 'New Hampshire'),
    )

    name = models.CharField(max_length=100)
    geom =  models.MultiPolygonField(srid=4326, null=True, blank=True)
    state = models.CharField(max_length=50, choices=STATES, null=False, blank=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Landmark(models.Model):
    STATES = (
        ('ME', 'Maine'),
        ('MA', 'Massachusetts'),
        ('NH', 'New Hampshire'),
    )

    name = models.CharField(max_length=100)
    coords =  models.PointField(srid=4326, null=True, blank=True)
    state = models.CharField(max_length=50, choices=STATES, null=False, blank=True, default='ME')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
