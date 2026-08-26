import json

from django.db import models
from django.db.models import (
    F,
    OuterRef,
    Subquery,
    Max,
    Window,
    Avg,
    BigIntegerField,
    Func,
)
from django.contrib.gis.db.models import Extent
from django.apps import apps
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import GeoHash, SnapToGrid

from habhub.core.models import TargetSpecies, Metric, DataLayer


class ExtractSpeciesMetricValue(Func):
    # Pull a single metric value out of a Bin's `cell_concentration_data` JSON array by
    # matching the array element whose "species" field equals `species_id`, instead of by
    # array position. Position isn't a stable species identifier: the array is built by
    # iterating TargetSpecies.objects.all() at the time a Bin's metrics were (re)calculated,
    # so a Bin's array position for a given species can shift relative to newer bins
    # whenever a TargetSpecies row is added/removed/renamed and older bins aren't
    # recalculated (see habhub.core.models.TargetSpecies.save()).
    output_field = BigIntegerField()

    def __init__(self, json_field, species_id, metric_id, **extra):
        self.species_id = species_id
        self.metric_id = metric_id
        super().__init__(json_field, **extra)

    def as_sql(self, compiler, connection, **extra_context):
        lhs, params = compiler.compile(self.source_expressions[0])
        # jsonpath key names must be literal (they can't be passed as bind parameters), so
        # the metric_id -- a trusted, admin-managed identifier -- is escaped and inlined.
        # The species_id value is passed as a proper bound parameter via jsonpath's "vars".
        safe_metric_id = self.metric_id.replace("\\", "\\\\").replace('"', '\\"')
        path = f'$[*] ? (@.species == $sp)."{safe_metric_id}"'
        sql = (
            f"(jsonb_path_query_first({lhs}, %s::jsonpath, %s::jsonb, true)::text)"
            "::bigint"
        )
        return sql, [*params, path, json.dumps({"sp": self.species_id})]


class BinQuerySet(models.QuerySet):
    def add_grid_metrics_data(self, grid_level=0.5):
        # custom query to collect all Bins by square spatial grid, then annotate aggregated
        # data values for all Bins in each square (max, mean) for each species.
        # Use the Window function to partition data by each grid square.
        # Returns (queryset, field_map): field_map tells callers which output column holds
        # the max/mean for each (species_id, metric_id) pair, since the column names
        # themselves are opaque (species_id/metric_id values can contain "_"/"-" and so
        # aren't safe to embed directly in an annotation alias).
        species_list = list(TargetSpecies.objects.values_list("species_id", flat=True))
        metrics = (
            Metric.objects.filter(data_layers__belongs_to_app=DataLayer.IFCB_DATASETS)
            .values("metric_id")
            .distinct()
        )

        field_list = ["grid", "geohash"]
        field_map = []

        grid_qs = self.annotate(grid=SnapToGrid("geom", grid_level))
        # add a Geohash anotation to server as unique IDfor API response/requests
        grid_qs = grid_qs.annotate(geohash=GeoHash("grid", 5))

        counter = 0
        for species_id in species_list:
            for metric in metrics:
                val_name = f"f{counter}_val"
                max_name = f"f{counter}_max"
                mean_name = f"f{counter}_mean"
                counter += 1

                field_list.extend([max_name, mean_name])
                field_map.append(
                    {
                        "species_id": species_id,
                        "metric_id": metric["metric_id"],
                        "max_field": max_name,
                        "mean_field": mean_name,
                    }
                )

                max_by_grid_square = Window(
                    expression=Max(val_name),
                    partition_by=F("grid"),
                )

                mean_by_grid_square = Window(
                    expression=Avg(val_name),
                    partition_by=F("grid"),
                )

                get_data_value = ExtractSpeciesMetricValue(
                    "cell_concentration_data", species_id, metric["metric_id"]
                )

                # use ** to unpack dicts to use dynamic variable names as we loop through the species/metrics
                grid_qs = (
                    grid_qs.annotate(**{val_name: get_data_value})
                    .annotate(**{max_name: max_by_grid_square})
                    .annotate(**{mean_name: mean_by_grid_square})
                )

        grid_qs = grid_qs.values(*field_list).distinct("grid").order_by("grid")

        return grid_qs, field_map

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
        print(f"grid_qs count 1: {grid_qs.count()}")
        # add a Geohash anotation to server as unique IDfor API response/requests,
        # then filter by the geohash from API request
        grid_qs = grid_qs.annotate(geohash=GeoHash("grid", 5)).filter(geohash=geohash)
        print(f"grid_qs count 2: {grid_qs.count()}")

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
