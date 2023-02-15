from django.db.models.expressions import ExpressionWrapper
from statistics import mean
from collections import OrderedDict

from rest_framework import serializers
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
)
from rest_framework_gis.fields import GeometryField
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.db.models import Extent
from django.db.models import Avg, Max, F

from ..models import Dataset, Bin
from habhub.core.models import TargetSpecies, Metric, DataLayer


class BinSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Bin
        geo_field = "geom"
        fields = [
            "pid",
            "geom",
            "dataset",
            "sample_time",
            "species_found",
            "cell_concentration_data",
        ]


class DatasetListSerializer(GeoFeatureModelSerializer):
    max_mean_values = serializers.SerializerMethodField("get_max_mean_values")

    class Meta:
        model = Dataset
        geo_field = "geom"
        fields = [
            "id",
            "name",
            "location",
            "dashboard_id_name",
            "geom",
            "max_mean_values",
        ]

    def get_max_mean_values(self, obj):
        return obj.get_max_mean_values()


class DatasetDetailSerializer(DatasetListSerializer):
    timeseries_data = serializers.SerializerMethodField("get_datapoints")

    class Meta(DatasetListSerializer.Meta):
        fields = DatasetListSerializer.Meta.fields + [
            "timeseries_data",
        ]

    def __init__(self, *args, **kwargs):
        super(DatasetDetailSerializer, self).__init__(*args, **kwargs)

        if "context" in kwargs:
            if "request" in kwargs["context"]:
                exclude_dataseries = kwargs["context"]["request"].query_params.get(
                    "exclude_dataseries", None
                )
                if exclude_dataseries:
                    self.fields.pop("timeseries_data")

    def get_datapoints(self, obj):
        concentration_timeseries = []
        metrics = obj.get_data_layer_metrics()
        # set up data structure to store results
        for species in TargetSpecies.objects.all():
            dict = {
                "species": species.species_id,
                "species_display": species.display_name,
                "data": [],
            }
            concentration_timeseries.append(dict)

        for bin in obj.bins.all():
            date_str = bin.sample_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            for datapoint in bin.cell_concentration_data:

                for (index, data) in enumerate(concentration_timeseries):
                    if data["species"] == datapoint["species"]:
                        data_dict = {
                            "sample_time": date_str,
                            "bin_pid": bin.pid,
                            "metrics": [],
                        }

                        for metric in metrics:
                            metric_value = 0

                            if metric.metric_id in datapoint:
                                metric_value = int(datapoint[metric.metric_id])

                            metric_obj = {
                                "metric_id": metric.metric_id,
                                "metric_name": metric.name,
                                "value": metric_value,
                                "units": metric.units,
                            }
                            data_dict["metrics"].append(metric_obj)

                        concentration_timeseries[index]["data"].append(data_dict)

        return concentration_timeseries


class DatasetAggSerializer(GeoFeatureModelSerializer):
    max_mean_values = serializers.SerializerMethodField("get_max_mean_values")

    class Meta:
        model = Dataset
        geo_field = "geom"
        fields = [
            "id",
            "name",
            "location",
            "dashboard_id_name",
            "geom",
            "max_mean_values",
        ]

    def get_max_mean_values(self, obj):
        max_mean_values = []
        group_qs = (
            obj.aggregate_dataset_metrics.values(
                "species__species_id",
            )
            .order_by("species")
            .annotate(
                cell_concentration_mean=Avg("cell_concentration_mean"),
                cell_concentration_max=Max("cell_concentration_max"),
                biovolume_mean=Avg("biovolume_mean"),
                biovolume_max=Max("biovolume_max"),
                # display_name=F("species__display_name"),
            )
        )

        for item in group_qs:
            maxmean_obj = {
                "species": item["species__species_id"],
                "data": [
                    {
                        "metricId": "biovolume",
                        "metricName": "Biovolume",
                        "maxValue": item["biovolume_max"],
                        "meanValue": item["biovolume_mean"],
                        "units": "cubic microns/L",
                    },
                    {
                        "metricId": "cell_concentration",
                        "metricName": "Cell Concentration",
                        "maxValue": item["cell_concentration_max"],
                        "meanValue": item["cell_concentration_mean"],
                        "units": "cells/L",
                    },
                ],
            }
            max_mean_values.append(maxmean_obj)
        return max_mean_values


class BinSpatialGridSerializer(serializers.Serializer):
    features = serializers.SerializerMethodField("get_grid_center_points")

    def to_representation(self, instance):
        data = super(BinSpatialGridSerializer, self).to_representation(instance)
        # must be "FeatureCollection" according to GeoJSON spec
        res = OrderedDict()
        # required type attribute
        # must be "Feature" according to GeoJSON spec
        res["type"] = "FeatureCollection"
        # add metadata attribute, optional for GeoJSON
        metadata = OrderedDict()
        for k, v in data.items():
            if k != "features":
                metadata[k] = data[k]
        res["metadata"] = metadata
        # required features attribute
        # MUST be present in output according to GeoJSON spec
        res["features"] = data["features"]
        return res

    def get_grid_center_points(self, obj):
        default_grid_level = 0.5
        features = []
        grid_level = self.context["request"].query_params.get(
            "grid_level", default_grid_level
        )

        try:
            grid_level = float(grid_level)
        except ValueError as e:
            grid_level = default_grid_level

        if not obj.exists():
            return features

        geo_field = GeometryField()
        # use custom queryset to build geospatial grid data
        grid_qs = obj.add_grid_metrics_data(grid_level)

        for square in grid_qs:
            feature = OrderedDict()
            # required type attribute
            # must be "Feature" according to GeoJSON spec
            feature["type"] = "Feature"
            # set id to be unique geohash
            feature["id"] = square["geohash"]
            # required geometry attribute
            # MUST be present in output according to GeoJSON spec
            geo_field = GeometryField()
            feature["geometry"] = geo_field.to_representation(square["grid"])
            # set GeoJSON properties
            properties = OrderedDict()
            properties["max_mean_values"] = self.format_max_mean(square)
            feature["properties"] = properties
            features.append(feature)

        return features

    def format_max_mean(self, square):
        target_list = TargetSpecies.objects.values_list("species_id", flat=True)
        index_list = [*range(0, target_list.count(), 1)]

        metrics = Metric.objects.filter(
            data_layers__belongs_to_app=DataLayer.IFCB_DATASETS
        ).distinct()
        max_mean_values = []

        # set up initial data structure
        for species in target_list:
            data_dict = {"species": species, "data": []}
            for metric in metrics:
                metric_data = {
                    "metric_id": metric.metric_id,
                    "metric_name": metric.name,
                    "max_value": 0,
                    "mean_value": 0,
                    "units": metric.units,
                }
                data_dict["data"].append(metric_data)
            max_mean_values.append(data_dict)

        # regroup the query results by species is using index numbers
        data_by_index = []
        for i in index_list:
            list_item = {"species": None, "data": []}
            for key, val in square.items():
                # get the species numeric key by splitting the string
                species_key = key.split("_")[0]

                if str(i) == species_key:
                    # get the species ID for the index, else add it to the data list as it's a metric
                    if "species" in key:
                        list_item["species"] = val
                    else:
                        data_item = {key: val}
                        list_item["data"].append(data_item)
            data_by_index.append(list_item)

        for item in max_mean_values:
            res = next(
                (data for data in data_by_index if data["species"] == item["species"]),
                None,
            )
            if res:
                for metric in item["data"]:
                    for d in res["data"]:
                        if metric["metric_id"] in list(d.keys())[0]:
                            if "max" in list(d.keys())[0]:
                                metric["max_value"] = list(d.values())[0]
                            elif "mean" in list(d.keys())[0]:
                                metric["mean_value"] = list(d.values())[0]

        return max_mean_values


class BinSpatialGridDetailSerializer(serializers.Serializer):
    geohash = serializers.SerializerMethodField("get_geohash")
    properties = serializers.SerializerMethodField("get_properties")

    def to_representation(self, instance):
        # format response to GeoJSON
        data = super(BinSpatialGridDetailSerializer, self).to_representation(instance)
        # must be "FeatureCollection" according to GeoJSON spec
        res = OrderedDict()
        # required type attribute
        # must be "Feature" according to GeoJSON spec
        res["type"] = "Feature"
        # set id to be unique geohash
        res["id"] = data["geohash"]
        # required features attribute
        # MUST be present in output according to GeoJSON spec
        # required geometry attribute
        geo_field = GeometryField()
        res["geometry"] = geo_field.to_representation(data["properties"]["geometry"])
        # set GeoJSON properties
        properties = OrderedDict()
        properties["timeseries_data"] = data["properties"]["timeseries_data"]
        res["properties"] = properties
        return res

    def get_geohash(self, obj):
        return self.context["geohash"]

    def get_properties(self, obj):
        timeseries_data = []
        geohash = self.context["geohash"]
        default_grid_level = 0.5
        grid_level = self.context["request"].query_params.get(
            "grid_level", default_grid_level
        )

        try:
            grid_level = float(grid_level)
        except ValueError as e:
            grid_level = default_grid_level

        if not obj.exists():
            return timeseries_data

        # use custom queryset to build geospatial grid data,
        # get all Bins that match the Geohash of the requested center point
        grid_qs = obj.add_single_grid_metrics_data(geohash, grid_level)
        # get the lat/long Point object from query results
        geometry = grid_qs.first().grid
        # set up data structure to store results
        metrics = Metric.objects.filter(
            data_layers__belongs_to_app=DataLayer.IFCB_DATASETS
        ).distinct()

        for species in TargetSpecies.objects.all():
            dict = {
                "species": species.species_id,
                "species_display": species.display_name,
                "data": [],
            }
            timeseries_data.append(dict)

        for bin in grid_qs.all():
            date_str = bin.sample_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            for datapoint in bin.cell_concentration_data:
                for (index, data) in enumerate(timeseries_data):
                    if data["species"] == datapoint["species"]:
                        data_dict = {
                            "sample_time": date_str,
                            "bin_pid": bin.pid,
                            "metrics": [],
                        }

                        for metric in metrics:
                            metric_value = 0

                            if metric.metric_id in datapoint:
                                metric_value = int(datapoint[metric.metric_id])

                            metric_obj = {
                                "metric_id": metric.metric_id,
                                "metric_name": metric.name,
                                "value": metric_value,
                                "units": metric.units,
                            }
                            data_dict["metrics"].append(metric_obj)

                        timeseries_data[index]["data"].append(data_dict)

        return {"timeseries_data": timeseries_data, "geometry": geometry}
