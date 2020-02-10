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

    class Meta:
        ordering = ['state', 'name']

    def __str__(self):
        return self.name

    def get_current_status(self):
        events_qs = self.closure_data_points.all()
        if events_qs:
            for event in events_qs:
                if event.get_current_status() == 'Closed':
                    status = 'Closed'
                    break
                else:
                    status = 'Open'
        else:
            status = 'Open'
        return status


class Landmark(models.Model):
    STATES = (
        ('ME', 'Maine'),
        ('MA', 'Massachusetts'),
        ('NH', 'New Hampshire'),
    )

    name = models.CharField(max_length=100)
    geom =  models.PointField(srid=4326, null=True, blank=True)
    state = models.CharField(max_length=50, choices=STATES, null=False, blank=True, default='ME')
    shellfish_areas = models.ManyToManyField(ShellfishArea, related_name='landmarks')

    class Meta:
        ordering = ['name']

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
    data_source = models.CharField(max_length=255, null=False, blank=True)
    shellfish_areas = models.ManyToManyField(ShellfishArea, related_name='closure_notices')
    border_east = models.ManyToManyField(Landmark, related_name='closure_notices_east', null=True, blank=True)
    border_west = models.ManyToManyField(Landmark, related_name='closure_notices_west', null=True, blank=True)
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

    # Custom save method to create granular ClosureDataEvent objects
    def save(self, *args, **kwargs):
        super(ClosureNotice, self).save(*args, **kwargs)
        notice_obj = self
        if notice_obj.pk:
            events_qs = ClosureDataEvent.objects.filter(closure_notice=notice_obj)
            events_qs.delete()

        for shellfish_area in notice_obj.shellfish_areas.all():
            for species in notice_obj.species.all():
                print(shellfish_area)
                print(species)
                event = ClosureDataEvent.objects.create(closure_notice=notice_obj,
                                                        shellfish_area=shellfish_area,
                                                        species=species,
                                                        effective_date=notice_obj.effective_date,
                                                        notice_action=notice_obj.notice_action,
                                                        causative_organism=notice_obj.causative_organism)


class ClosureNoticeMaine(ClosureNotice):
    class Meta:
        proxy = True
        verbose_name = 'Closure notice (Maine)'
        verbose_name_plural = 'Closure notices (Maine)'


class ClosureDataEvent(models.Model):
    closure_notice = models.ForeignKey(ClosureNotice, related_name='closure_data_points',
                                       on_delete=models.CASCADE, null=False)
    shellfish_area = models.ForeignKey(ShellfishArea, related_name='closure_data_points',
                                       on_delete=models.CASCADE, null=False)
    species = models.ForeignKey(Species, related_name='closure_data_points',
                                on_delete=models.CASCADE, null=False)
    effective_date = models.DateField(default=timezone.now)
    notice_action = models.CharField(max_length=50, default='Open')
    causative_organism = models.ForeignKey(CausativeOrganism, related_name='closure_data_points',
                                           on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return '%s - %s - %s' % (self.closure_notice, self.shellfish_area, self.species)

    # Get current status of this Closure Event
    def get_current_status(self):
        if self.notice_action == 'Closed':
            try:
                open_notice_obj = ClosureDataEvent.objects.filter(shellfish_area=self.shellfish_area) \
                                                              .filter(species=self.species) \
                                                              .filter(effective_date__gte=self.effective_date) \
                                                              .filter(notice_action='Open') \
                                                              .earliest('effective_date')
                current_status = 'Open'
            except ClosureDataEvent.DoesNotExist:
                current_status = 'Closed'
        else:
            current_status = 'Open'
        return current_status

    # Get the total duration of the Closure Event
    def get_closure_duration(self):
        if self.notice_action == 'Closed':
            try:
                open_notice_obj = ClosureDataEvent.objects.filter(shellfish_area=self.shellfish_area) \
                                                          .filter(species=self.species) \
                                                          .filter(effective_date__gte=self.effective_date) \
                                                          .filter(notice_action='Open') \
                                                          .earliest('effective_date')
                duration = open_notice_obj.effective_date - self.effective_date
            except:
                duration = None
        else:
            duration = None
        return duration


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
