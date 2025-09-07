from django.db import models
from django.db.models import (
    F,
    OuterRef,
    Subquery,
    Max,
    Window,
    Avg,
    BigIntegerField,
    TextField,
)
from django.db.models.functions import Cast
from django.contrib.gis.db.models import Extent
from django.apps import apps
from django.contrib.gis.geos import Point
from django.db.models.fields.json import KeyTextTransform
from django.contrib.gis.db.models.functions import GeoHash, SnapToGrid

from habhub.core.models import TargetSpecies, Metric, DataLayer


class BinQuerySet(models.QuerySet):
    def add_grid_metrics_data(self, grid_level=0.5):
        # custom query to collect all Bins by square spatial grid,
        # then annotate aggregated data values for all Bins in each square (max, mean) for each species.
        # Use the Window function to partition data by each grid square
        target_count = TargetSpecies.objects.all().count()
        metrics = (
            Metric.objects.filter(data_layers__belongs_to_app=DataLayer.IFCB_DATASETS)
            .values("metric_id")
            .distinct()
        )

        index_list = [*range(0, target_count, 1)]
        field_list = ["grid", "geohash"]

        grid_qs = self.annotate(grid=SnapToGrid("geom", grid_level))
        # add a Geohash anotation to server as unique IDfor API response/requests
        grid_qs = grid_qs.annotate(geohash=GeoHash("grid", 5))

        for i in index_list:
            for metric in metrics:
                val_name = f"{i}_val_{metric['metric_id']}"
                max_name = f"{i}_max_{metric['metric_id']}"
                mean_name = f"{i}_mean_{metric['metric_id']}"
                species_name = f"{i}_species"

                field_list.extend([max_name, mean_name, species_name])

                max_by_grid_square = Window(
                    expression=Max(val_name),
                    partition_by=F("grid"),
                )

                mean_by_grid_square = Window(
                    expression=Avg(val_name),
                    partition_by=F("grid"),
                )
                # data is in array within JSON field, need to use nested KeyTextTransform to get each array item
                get_data_value = Cast(
                    KeyTextTransform(
                        metric["metric_id"],
                        (KeyTextTransform(str(i), "cell_concentration_data")),
                    ),
                    BigIntegerField(),
                )

                get_species_value = Cast(
                    KeyTextTransform(
                        "species",
                        (KeyTextTransform(str(i), "cell_concentration_data")),
                    ),
                    TextField(),
                )
                # use ** to unpack dicts to use dynamic variable names as we loop through the species/metrics
                grid_qs = (
                    grid_qs.annotate(**{val_name: get_data_value})
                    .annotate(**{max_name: max_by_grid_square})
                    .annotate(**{mean_name: mean_by_grid_square})
                    .annotate(**{species_name: get_species_value})
                )

        grid_qs = grid_qs.values(*field_list).distinct("grid").order_by("grid")
        return grid_qs

    def add_single_grid_metrics_data(
        self,
        geohash,
        grid_level=0.5,
    ):
        # custom query to collect all Bins by single square spatial grid,
        # grid is ID'ed by unique Geohash created in the "add_grid_metrics_data" method
        target_count = TargetSpecies.objects.all().count()
        metrics = (
            Metric.objects.filter(data_layers__belongs_to_app=DataLayer.IFCB_DATASETS)
            .values("metric_id")
            .distinct()
        )
        grid_qs = self.annotate(grid=SnapToGrid("geom", grid_level))

        # add a Geohash anotation to server as unique IDfor API response/requests,
        # then filter by the geohash from API request
        grid_qs = grid_qs.annotate(geohash=GeoHash("grid", 5)).filter(geohash=geohash)

        return grid_qs


class DatasetQuerySet(models.QuerySet):
    def add_bins_geo_extent(self, date_q_filters=None):
        Bin = apps.get_model(app_label="ifcb_datasets", model_name="Bin")
        zero_pt = Point(0, 0)
        # set up the Subquery query with conditional date filter
        bin_query = Bin.objects.filter(dataset=OuterRef("id"))

        if date_q_filters:
            bin_query = bin_query.filter(date_q_filters)

        bin_query = (
            bin_query.filter(geom__isnull=False)
            .filter(cell_concentration_data__isnull=False)
            .exclude(geom=zero_pt)
        )

        # now aggregate all filtered Bins to get Extent, but use annotate in subquery
        bin_query = (
            bin_query.values("dataset_id")  # group by dataset
            .order_by()  # reset ordering
            .annotate(bins_geo_extent=Extent("geom"))
            .values("bins_geo_extent")[:1]
        )

        return self.annotate(bins_geo_extent=Subquery(bin_query))
