import datetime
from datetime import timedelta

from django.contrib.gis.db import models
from django.utils import timezone
from django.utils.html import format_html
from djgeojson.fields import PointField, PolygonField

# Closure app models.


class ShellfishArea(models.Model):
    STATES = (
        ("ME", "Maine"),
        ("MA", "Massachusetts"),
        ("NH", "New Hampshire"),
    )

    name = models.CharField(max_length=100, db_index=True)
    state = models.CharField(
        max_length=50, choices=STATES, null=False, blank=True, db_index=True
    )
    geom = models.MultiPolygonField(srid=4326)
    geom_center_point = models.PointField(srid=4326, null=True, blank=True)
    acres = models.DecimalField(max_digits=19, decimal_places=10, null=True)
    area_description = models.CharField(max_length=1000, null=False, blank=True)
    area_class = models.CharField(max_length=100, null=False, blank=True)
    atlas_key = models.CharField(max_length=100, null=False, blank=True)
    is_atlas_combined_area = models.BooleanField(default=False)

    class Meta:
        ordering = ["state", "name"]

    def __str__(self):
        return self.name

    # Custom save method to add Geometric center point for each polygon
    def save(self, *args, **kwargs):
        self.geom_center_point = self.geom.centroid
        super(ShellfishArea, self).save(*args, **kwargs)

    def get_current_status(self):
        events_qs = self.closure_data_points.all()
        if events_qs:
            for event in events_qs:
                if event.get_current_status() == "Closed":
                    status = "Closed"
                    break
                else:
                    status = "Open"
        else:
            status = "Open"
        return status


class ShellfishAreaImport(models.Model):
    STATES = (
        ("ME", "Maine"),
        ("MA", "Massachusetts"),
        ("NH", "New Hampshire"),
    )

    name = models.CharField(max_length=100, db_index=True)
    state = models.CharField(
        max_length=50, choices=STATES, null=False, blank=True, db_index=True
    )
    geom = models.MultiPolygonField(srid=4326)
    acres = models.DecimalField(max_digits=19, decimal_places=10, null=True)
    area_description = models.CharField(max_length=1000, null=False, blank=True)
    area_class = models.CharField(max_length=100, null=False, blank=True)
    atlas_key = models.CharField(max_length=100, null=False, blank=True)

    class Meta:
        ordering = ["state", "name"]

    def __str__(self):
        return self.name


class Landmark(models.Model):
    STATES = (
        ("ME", "Maine"),
        ("MA", "Massachusetts"),
        ("NH", "New Hampshire"),
    )

    name = models.CharField(max_length=100)
    geom = models.PointField(srid=4326, null=True, blank=True)
    state = models.CharField(
        max_length=50, choices=STATES, null=False, blank=True, default="ME"
    )
    shellfish_areas = models.ManyToManyField(ShellfishArea, related_name="landmarks")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Species(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Species"

    def __str__(self):
        return self.name


class CausativeOrganism(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ClosureNotice(models.Model):
    NOTICE_ACTION = (
        ("Open", "Open"),
        ("Closed", "Closed"),
    )

    SYNDROME = (
        ("PSP", "Paralytic Shellfish Poison (PSP)"),
        ("DSP", "Diarrhetic shellfish poisoning (DSP)"),
        ("ASP", "Amnesic shellfish poisoning (ASP)"),
    )

    title = models.CharField(max_length=100)
    created_date = models.DateField(default=timezone.now)
    effective_date = models.DateField(default=timezone.now)
    data_source = models.CharField(max_length=255, null=False, blank=True)
    shellfish_areas = models.ManyToManyField(
        ShellfishArea, related_name="closure_notices"
    )
    border_east = models.ManyToManyField(
        Landmark, related_name="closure_notices_east", blank=True
    )
    border_west = models.ManyToManyField(
        Landmark, related_name="closure_notices_west", blank=True
    )
    custom_borders = models.MultiLineStringField(srid=4326, null=True, blank=True)
    custom_geom = models.MultiPolygonField(srid=4326, null=True, blank=True)
    species = models.ManyToManyField(Species, related_name="closure_notices")
    notice_action = models.CharField(
        max_length=50, choices=NOTICE_ACTION, default="Open"
    )
    syndrome = models.CharField(
        max_length=50, choices=SYNDROME, null=False, blank=True, default="PSP"
    )
    causative_organism = models.ForeignKey(
        CausativeOrganism,
        related_name="closure_notices",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    document = models.FileField(upload_to="closure_notices/", null=True, blank=True)
    comments = models.TextField(null=False, blank=True)

    class Meta:
        ordering = ["-effective_date", "title"]
        get_latest_by = "effective_date"

    def __str__(self):
        return self.title

    def get_shellfish_areas(self):
        return ", ".join([str(area) for area in self.shellfish_areas.all()])

    get_shellfish_areas.short_description = "Shellfish Areas"

    def get_state(self):
        area = self.shellfish_areas.first()
        if area:
            state = area.get_state_display()
        else:
            state = None
        return state

    get_state.short_description = "State"

    # Get the total duration of the Closure Notice by finding the longest ClosureEvent
    def get_total_closure_duration(self):
        closure_events_qs = self.closure_data_events.all()
        if closure_events_qs:
            durations = []
            for event in closure_events_qs:
                try:
                    event_duration = event.get_closure_duration().days
                    durations.append(event_duration)
                except:
                    durations = None
                    total_duration = "Ongoing"
            if durations:
                total_duration = "%s days" % (max(durations))
        else:
            total_duration = None

        return total_duration

    # Custom save method to create granular ClosureDataEvent objects
    def save(self, *args, **kwargs):
        super(ClosureNotice, self).save(*args, **kwargs)
        notice_obj = self
        if notice_obj.pk:
            events_qs = ClosureDataEvent.objects.filter(closure_notice=notice_obj)
            events_qs.delete()

        for shellfish_area in notice_obj.shellfish_areas.all():
            for species in notice_obj.species.all():
                event = ClosureDataEvent.objects.create(
                    closure_notice=notice_obj,
                    shellfish_area=shellfish_area,
                    species=species,
                    effective_date=notice_obj.effective_date,
                    notice_action=notice_obj.notice_action,
                    causative_organism=notice_obj.causative_organism,
                )


class ClosureNoticeMaine(ClosureNotice):
    class Meta:
        proxy = True
        verbose_name = "Closure notice (Maine)"
        verbose_name_plural = "Closure notices (Maine)"


class ClosureDataEvent(models.Model):
    closure_notice = models.ForeignKey(
        ClosureNotice,
        related_name="closure_data_events",
        on_delete=models.CASCADE,
        null=False,
    )
    shellfish_area = models.ForeignKey(
        ShellfishArea,
        related_name="closure_data_events",
        on_delete=models.CASCADE,
        null=False,
    )
    species = models.ForeignKey(
        Species,
        related_name="closure_data_events",
        on_delete=models.CASCADE,
        null=False,
    )
    effective_date = models.DateField(default=timezone.now)
    notice_action = models.CharField(max_length=50, default="Open")
    duration = models.DurationField(
        default=timedelta(minutes=0), null=False, blank=True
    )
    causative_organism = models.ForeignKey(
        CausativeOrganism,
        related_name="closure_data_events",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        get_latest_by = "effective_date"

    def __str__(self):
        return "%s - %s - %s" % (self.closure_notice, self.shellfish_area, self.species)

    # Custom save method to update closure duration
    def save(self, *args, **kwargs):
        if self.notice_action == "Open":
            duration = timedelta(minutes=0)
            try:
                # get the closure event that started the closure
                close_notice_obj = (
                    ClosureDataEvent.objects.filter(shellfish_area=self.shellfish_area)
                    .filter(species=self.species)
                    .filter(effective_date__lte=self.effective_date)
                    .filter(notice_action="Closed")
                    .latest()
                )
                print(close_notice_obj.id)
                duration = self.effective_date - close_notice_obj.effective_date
                close_notice_obj.duration = duration
                close_notice_obj.save()
                self.duration = duration
            except:
                pass
        super(ClosureDataEvent, self).save(*args, **kwargs)

    # Get current status of this Closure Event
    def get_current_status(self):
        if self.notice_action == "Closed":
            try:
                open_notice_obj = (
                    ClosureDataEvent.objects.filter(shellfish_area=self.shellfish_area)
                    .filter(species=self.species)
                    .filter(effective_date__gte=self.effective_date)
                    .filter(notice_action="Open")
                    .earliest("effective_date")
                )
                current_status = "Open"
            except ClosureDataEvent.DoesNotExist:
                current_status = "Closed"
        else:
            current_status = "Open"
        return current_status

    # Get the total duration of the Closure Event
    @property
    def get_closure_duration(self):
        if self.duration > timedelta(minutes=0):
            return f"{self.duration.days} days"
        return "Ongoing"


class ExceptionArea(models.Model):
    title = models.CharField(max_length=100)
    species = models.ManyToManyField(Species, related_name="exception_areas")
    closure_notice = models.ForeignKey(
        ClosureNotice,
        related_name="exception_areas",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    description = models.TextField(null=False, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class BaseAreaShape(models.Model):
    STATES = (
        ("ME", "Maine"),
        ("MA", "Massachusetts"),
        ("NH", "New Hampshire"),
    )

    name = models.CharField(max_length=100)
    geom = models.MultiPolygonField(srid=4326, null=True, blank=True)
    state = models.CharField(
        max_length=50, choices=STATES, null=False, blank=True, db_index=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
