from colour import Color
from decimal import Decimal
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.contrib.postgres.fields import ArrayField
from django.core.cache import cache
from colorfield.fields import ColorField

from config import celery_app
from .utils import linear_gradient
from habhub.ifcb_datasets.tasks import recalculate_metrics, reset_ifcb_dataset_data


class TargetSpecies(models.Model):
    # Model to configure Target HAB species for HABhub to monitor
    # Used for all data layers

    MARINE = "Marine"
    FRESHWATER = "Freshwater"
    ENVIRONMENT_CHOICES = [
        (MARINE, "Marine"),
        (FRESHWATER, "Freshwater"),
    ]

    # Species Type (HAB or Other)
    HAB = "HAB"
    OTHER = "Other"
    SPECIES_TYPE_CHOICES = [
        (HAB, "HAB"),
        (OTHER, "Other"),
    ]

    # species_id needs to match the Autoclass files in the IFCB Dashboard
    species_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Needs to match the species ID used in the Autoclass files from the IFCB Dashboard",
    )
    display_name = models.CharField(max_length=100, db_index=True)
    syndrome = models.CharField(max_length=100, blank=True)
    primary_color = ColorField(default="#FF0000")
    color_gradient = ArrayField(
        models.CharField(max_length=7), null=True, blank=True, default=None
    )
    species_type = models.CharField(
        max_length=20,
        choices=SPECIES_TYPE_CHOICES,
        default=HAB,
    )
    species_environment = models.CharField(
        max_length=20,
        choices=ENVIRONMENT_CHOICES,
        default=MARINE,
    )
    autoclass_threshold = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        ordering = ["species_id"]
        verbose_name_plural = "Target Species"

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        # Custom save method to create color gradient based on primary_color
        dark_shade = Color(self.primary_color)
        dark_shade.luminance = 0.35
        color_gradient = linear_gradient(self.primary_color, "#FFFFFF", 5)
        # remove white
        color_gradient.pop()
        # add dark_shade
        color_gradient.insert(0, dark_shade.hex)
        color_gradient.reverse()
        self.color_gradient = color_gradient
        # Check if new species added, start new data ingestion
        # Also seed to check if autoclass_threshold value has changed
        # if yes, IFCB metric data needs to be reset
        start_new_data_ingest = False
        threshold_changed = False
        if self.pk is not None:
            orig = TargetSpecies.objects.get(pk=self.pk)
            if orig.autoclass_threshold != self.autoclass_threshold:
                threshold_changed = True
        else:
            # new item added
            print("NEW SPECIES ADDED")
            start_new_data_ingest = True

        super(TargetSpecies, self).save(*args, **kwargs)
        # trigger celery task to recalculate IFCB data
        if start_new_data_ingest:
            print("START NEW SPECIES DATA RUN ", self.species_id)
            # transaction.on_commit(
            #    lambda: reset_ifcb_dataset_data.delay(None, self.species_id)
            # )

        if threshold_changed:
            # search cache for any current tasks that are running for this species
            # revoke tasks to avoid endless queue
            cache_key = (
                f"habhub.ifcb_datasets.tasks.recalculate_metrics-{self.species_id}"
            )
            task_id = cache.get(cache_key)
            print("CACHE FOUND TASK ID: ", task_id)
            if task_id:
                print("REVOKING TASK: ", task_id)
                celery_app.control.revoke(task_id=task_id, terminate=True)
                cache.delete(cache_key)

            transaction.on_commit(lambda: recalculate_metrics.delay(self.species_id))


class DataLayer(models.Model):
    # Model to configure which Data Layers are active for the frontend client

    # Possible local "habhub" Django apps that layer can belong to
    IFCB_DATASETS = "ifcb_datasets"
    STATIONS = "stations"
    CLOSURES = "closures"
    APP_CHOICES = [
        (IFCB_DATASETS, "Ifcb_Datasets"),
        (STATIONS, "Stations"),
        (CLOSURES, "Closures"),
    ]

    layer_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=100, blank=True, db_index=True)
    belongs_to_app = models.CharField(
        max_length=100, db_index=True, choices=APP_CHOICES, default=IFCB_DATASETS
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Metric(models.Model):
    # Metrics available for different data layers
    metric_id = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    units = models.CharField(max_length=100, blank=True)
    data_layers = models.ManyToManyField(DataLayer, related_name="metrics")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class MapBookmark(models.Model):
    # data model to hold saved query variables to allow users to create bookmarkable links
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    species = ArrayField(models.CharField(max_length=50))
    data_layers = ArrayField(models.CharField(max_length=50))
    latitude = models.DecimalField(max_digits=8, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    zoom = models.DecimalField(max_digits=7, decimal_places=5)
    seasonal = models.BooleanField(default=False)
    exclude_month_range = models.BooleanField(default=False)
    max_mean = models.CharField(max_length=20, default="mean")
    active_features = models.JSONField(null=True, blank=True)
    relative_date_range = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"ID: {self.id}"
