from django.db.models.expressions import ExpressionWrapper
import s2sphere
from statistics import mean
from collections import OrderedDict

from rest_framework import serializers
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeometrySerializerMethodField,
)
from rest_framework_gis.fields import GeometryField
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.db.models import Extent

from ..models import Dataset, Bin
from habhub.core.models import TargetSpecies, Metric, DataLayer
from habhub.core.constants import IFCB_LAYER


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
                index = next(
                    (
                        index
                        for (index, data) in enumerate(concentration_timeseries)
                        if data["species"] == datapoint["species"]
                    ),
                    None,
                )

                if index:
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
                            "metric_name": metric.name,
                            "value": metric_value,
                            "units": metric.units,
                        }
                        data_dict["metrics"].append(metric_obj)

                    concentration_timeseries[index]["data"].append(data_dict)

        return concentration_timeseries


class SpatialDatasetSerializer(serializers.ModelSerializer):
    # bbox = GeometrySerializerMethodField()
    features = serializers.SerializerMethodField("get_grid_center_points")

    class Meta:
        model = Dataset
        fields = ["id", "name", "location", "dashboard_id_name", "features"]

    def to_representation(self, instance):
        data = super(SpatialDatasetSerializer, self).to_representation(instance)
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

    def convert_s2_point_to_latlng(self, s2_point):
        # utility function to convert S2 points to lat/lng
        coords = str(s2_point).split()[-1].split(",")
        lat_lng = {"lat": float(coords[0]), "long": float(coords[1])}
        return lat_lng

    def get_grid_center_points(self, obj):
        # run aggregate funtion on Bin queryset to get bounding box coords
        features = []
        zero_pt = Point(0, 0)

        if not obj.bins.exists():
            return features

        bins = obj.bins.filter(
            cell_concentration_data__isnull=False, geom_s2_token__isnull=False
        ).exclude(geom=zero_pt)
        # Extent returns (ne, sw) points of box
        bbbox_extent = bins.aggregate(Extent("geom"))
        print(bbbox_extent)
        # bin_tokens = bins.values_list('geom_s2_token', flat=True)
        # S2 functions to get even grid of polygons to cover bounding box
        r = s2sphere.RegionCoverer()
        r.min_level = 7
        r.max_level = 7
        p1 = s2sphere.LatLng.from_degrees(
            bbbox_extent["geom__extent"][1], bbbox_extent["geom__extent"][0]
        )
        p2 = s2sphere.LatLng.from_degrees(
            bbbox_extent["geom__extent"][3], bbbox_extent["geom__extent"][2]
        )
        print(p1)
        print(p2)
        covering = r.get_covering(s2sphere.LatLngRect.from_point_pair(p1, p2))

        """
        for cellid in covering:
            cell_center_ll = cellid.to_lat_lng()
            lat_lng = self.convert_s2_point_to_latlng(cell_center_ll)
            token = cellid.to_token()

            # get all Bins within this cell
            bins_in_cell = [token for token in bin_tokens if cellid.contains(s2sphere.CellId.from_token(token))]
            # get max/mean values for the cell
            #max_mean = obj.get_max_mean_values(query_by_token=bins_in_cell)
            #print(max_mean)
            if bins_in_cell:
                point = {
                    "token": token,
                    "lat": lat_lng["lat"],
                    "long": lat_lng["long"],
                    "bins": bins_in_cell
                }
                points.append(point)
        """
        # prepare OrderedDict geojson structure

        for cellid in covering:
            cell_center_ll = cellid.to_lat_lng()
            lat_lng = self.convert_s2_point_to_latlng(cell_center_ll)
            token = cellid.to_token()
            # Builds GEOS polygons out of cell vertices
            # use these polygons to query PostGIS
            vertices = [
                s2sphere.LatLng.from_point(s2sphere.Cell(cellid).get_vertex(v))
                for v in range(4)
            ]
            poly_points = []
            for v in vertices:
                # get just lat/long coords from S2 LatLng
                coords = str(v).split()[-1].split(",")
                point = Point(float(coords[1]), float(coords[0]))
                poly_points.append(point)
            # close the loop for a Polygon
            poly_points.append(poly_points[0])
            poly = Polygon(poly_points)
            centroid = poly.centroid

            # get all Bins within this cell
            bins_in_cell = bins.filter(geom__within=poly)

            if bins_in_cell.exists():
                max_mean = obj.get_max_mean_values(queryset=bins_in_cell)
                feature = OrderedDict()
                # required type attribute
                # must be "Feature" according to GeoJSON spec
                feature["type"] = "Feature"
                # required geometry attribute
                # MUST be present in output according to GeoJSON spec
                geo_field = GeometryField()
                feature["geometry"] = geo_field.to_representation(centroid)
                # set GeoJSON properties
                properties = OrderedDict()
                properties["s2_token"] = token
                properties["max_mean_values"] = max_mean
                feature["properties"] = properties
                #
                features.append(feature)

        return features


class SpatialBinSerializer(serializers.Serializer):
    # bbox = GeometrySerializerMethodField()
    features = serializers.SerializerMethodField("get_grid_center_points")

    def to_representation(self, instance):
        data = super(SpatialBinSerializer, self).to_representation(instance)
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

    def convert_s2_point_to_latlng(self, s2_point):
        # utility function to convert S2 points to lat/lng
        coords = str(s2_point).split()[-1].split(",")
        lat_lng = {"lat": float(coords[0]), "long": float(coords[1])}
        return lat_lng

    def get_grid_center_points(self, obj):
        # run aggregate funtion on Bin queryset to get bounding box coords
        features = []
        zero_pt = Point(0, 0)

        if not obj.exists():
            return features

        # Extent returns (ne, sw) points of box
        bbbox_extent = obj.aggregate(Extent("geom"))
        print(bbbox_extent)
        # bin_tokens = bins.values_list('geom_s2_token', flat=True)
        # S2 functions to get even grid of polygons to cover bounding box
        r = s2sphere.RegionCoverer()
        r.min_level = 7
        r.max_level = 7
        p1 = s2sphere.LatLng.from_degrees(
            bbbox_extent["geom__extent"][1], bbbox_extent["geom__extent"][0]
        )
        p2 = s2sphere.LatLng.from_degrees(
            bbbox_extent["geom__extent"][3], bbbox_extent["geom__extent"][2]
        )
        print(p1)
        print(p2)
        covering = r.get_covering(s2sphere.LatLngRect.from_point_pair(p1, p2))

        """
        for cellid in covering:
            cell_center_ll = cellid.to_lat_lng()
            lat_lng = self.convert_s2_point_to_latlng(cell_center_ll)
            token = cellid.to_token()

            # get all Bins within this cell
            bins_in_cell = [token for token in bin_tokens if cellid.contains(s2sphere.CellId.from_token(token))]
            # get max/mean values for the cell
            #max_mean = obj.get_max_mean_values(query_by_token=bins_in_cell)
            #print(max_mean)
            if bins_in_cell:
                point = {
                    "token": token,
                    "lat": lat_lng["lat"],
                    "long": lat_lng["long"],
                    "bins": bins_in_cell
                }
                points.append(point)
        """
        # prepare OrderedDict geojson structure

        for cellid in covering:
            cell_center_ll = cellid.to_lat_lng()
            lat_lng = self.convert_s2_point_to_latlng(cell_center_ll)
            token = cellid.to_token()
            # Builds GEOS polygons out of cell vertices
            # use these polygons to query PostGIS
            vertices = [
                s2sphere.LatLng.from_point(s2sphere.Cell(cellid).get_vertex(v))
                for v in range(4)
            ]
            poly_points = []
            for v in vertices:
                # get just lat/long coords from S2 LatLng
                coords = str(v).split()[-1].split(",")
                point = Point(float(coords[1]), float(coords[0]))
                poly_points.append(point)
            # close the loop for a Polygon
            poly_points.append(poly_points[0])
            poly = Polygon(poly_points)
            centroid = poly.centroid

            # get all Bins within this cell
            bins_in_cell = obj.filter(geom__within=poly)

            if bins_in_cell.exists():
                max_mean = self.get_max_mean_values(queryset=bins_in_cell)
                feature = OrderedDict()
                # required type attribute
                # must be "Feature" according to GeoJSON spec
                feature["type"] = "Feature"
                # required geometry attribute
                # MUST be present in output according to GeoJSON spec
                geo_field = GeometryField()
                feature["geometry"] = geo_field.to_representation(centroid)
                # set GeoJSON properties
                properties = OrderedDict()
                properties["s2_token"] = token
                properties["max_mean_values"] = max_mean
                feature["properties"] = properties
                #
                features.append(feature)

        return features

    def get_max_mean_values(self, queryset):
        bins_qs = queryset
        target_list = TargetSpecies.objects.values_list("species_id", flat=True)
        # set up data structure to store results
        concentration_values = []
        max_mean_values = []

        for species in target_list:
            concentration_dict = {"species": species, "values": []}
            concentration_values.append(concentration_dict)

        for bin in bins_qs:
            if bin.cell_concentration_data:
                for datapoint in bin.cell_concentration_data:
                    item = next(
                        (
                            item
                            for item in concentration_values
                            if item["species"] == datapoint["species"]
                        ),
                        None,
                    )

                    if item is not None:
                        item["values"].append(int(datapoint["cell_concentration"]))

        for item in concentration_values:
            if item["values"]:
                max_value = max(item["values"])
                mean_value = mean(item["values"])
            else:
                max_value = 0
                mean_value = 0

            data_dict = {
                "species": item["species"],
                "max_value": max_value,
                "mean_value": mean_value,
            }
            max_mean_values.append(data_dict)

        return max_mean_values


class BoundingBoxSerializer(serializers.Serializer):
    # max_bounding_box = GeometrySerializerMethodField()
    bounding_box = serializers.ListField(child=serializers.FloatField())

    def get_max_bounding_box(self, obj):
        return obj


class SpatialGridSerializer(serializers.Serializer):
    features = serializers.SerializerMethodField("get_grid_center_points")

    def to_representation(self, instance):
        data = super(SpatialGridSerializer, self).to_representation(instance)
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

    def convert_s2_point_to_latlng(self, s2_point):
        # utility function to convert S2 points to lat/lng
        coords = str(s2_point).split()[-1].split(",")
        lat_lng = {"lat": float(coords[0]), "long": float(coords[1])}
        return lat_lng

    def get_grid_center_points(self, obj):
        # run aggregate funtion on Bin queryset to get bounding box coords
        features = []
        grid_level = self.context["request"].query_params.get("grid_level", None)

        if grid_level:
            grid_level = int(grid_level)
        else:
            grid_level = 7

        if not obj.exists():
            return features

        # Extent returns (ne, sw) points of box
        bbbox_extent = obj.aggregate(Extent("geom"))
        print(bbbox_extent)
        # bin_tokens = bins.values_list('geom_s2_token', flat=True)
        # S2 functions to get even grid of polygons to cover bounding box
        r = s2sphere.RegionCoverer()
        r.min_level = grid_level
        r.max_level = grid_level
        p1 = s2sphere.LatLng.from_degrees(
            bbbox_extent["geom__extent"][1], bbbox_extent["geom__extent"][0]
        )
        p2 = s2sphere.LatLng.from_degrees(
            bbbox_extent["geom__extent"][3], bbbox_extent["geom__extent"][2]
        )
        covering = r.get_covering(s2sphere.LatLngRect.from_point_pair(p1, p2))

        """
        for cellid in covering:
            cell_center_ll = cellid.to_lat_lng()
            lat_lng = self.convert_s2_point_to_latlng(cell_center_ll)
            token = cellid.to_token()

            # get all Bins within this cell
            bins_in_cell = [token for token in bin_tokens if cellid.contains(s2sphere.CellId.from_token(token))]
            # get max/mean values for the cell
            #max_mean = obj.get_max_mean_values(query_by_token=bins_in_cell)
            #print(max_mean)
            if bins_in_cell:
                point = {
                    "token": token,
                    "lat": lat_lng["lat"],
                    "long": lat_lng["long"],
                    "bins": bins_in_cell
                }
                points.append(point)
        """
        # prepare OrderedDict geojson structure
        for cellid in covering:
            cell_center_ll = cellid.to_lat_lng()
            lat_lng = self.convert_s2_point_to_latlng(cell_center_ll)
            token = cellid.to_token()
            # Builds GEOS polygons out of cell vertices
            # use these polygons to query PostGIS
            vertices = [
                s2sphere.LatLng.from_point(s2sphere.Cell(cellid).get_vertex(v))
                for v in range(4)
            ]
            poly_points = []
            for v in vertices:
                # get just lat/long coords from S2 LatLng
                coords = str(v).split()[-1].split(",")
                point = Point(float(coords[1]), float(coords[0]))
                poly_points.append(point)
            # close the loop for a Polygon
            poly_points.append(poly_points[0])
            poly = Polygon(poly_points)
            centroid = poly.centroid

            # get all Bins within this cell
            bins_in_cell = obj.filter(geom__within=poly)

            if bins_in_cell.exists():
                max_mean = self.get_max_mean_values(queryset=bins_in_cell)
                feature = OrderedDict()
                # required type attribute
                # must be "Feature" according to GeoJSON spec
                feature["type"] = "Feature"
                # required geometry attribute
                # MUST be present in output according to GeoJSON spec
                geo_field = GeometryField()
                feature["geometry"] = geo_field.to_representation(centroid)
                # set GeoJSON properties
                properties = OrderedDict()
                properties["s2_token"] = token
                properties["grid_level"] = grid_level
                properties["max_mean_values"] = max_mean
                feature["properties"] = properties
                #
                features.append(feature)

        grid_level = 8
        r.min_level = grid_level
        r.max_level = grid_level
        covering = r.get_covering(s2sphere.LatLngRect.from_point_pair(p1, p2))
        # prepare OrderedDict geojson structure
        for cellid in covering:
            cell_center_ll = cellid.to_lat_lng()
            lat_lng = self.convert_s2_point_to_latlng(cell_center_ll)
            token = cellid.to_token()
            # Builds GEOS polygons out of cell vertices
            # use these polygons to query PostGIS
            vertices = [
                s2sphere.LatLng.from_point(s2sphere.Cell(cellid).get_vertex(v))
                for v in range(4)
            ]
            poly_points = []
            for v in vertices:
                # get just lat/long coords from S2 LatLng
                coords = str(v).split()[-1].split(",")
                point = Point(float(coords[1]), float(coords[0]))
                poly_points.append(point)
            # close the loop for a Polygon
            poly_points.append(poly_points[0])
            poly = Polygon(poly_points)
            centroid = poly.centroid

            # get all Bins within this cell
            bins_in_cell = obj.filter(geom__within=poly)

            if bins_in_cell.exists():
                max_mean = self.get_max_mean_values(queryset=bins_in_cell)
                feature = OrderedDict()
                # required type attribute
                # must be "Feature" according to GeoJSON spec
                feature["type"] = "Feature"
                # required geometry attribute
                # MUST be present in output according to GeoJSON spec
                geo_field = GeometryField()
                feature["geometry"] = geo_field.to_representation(centroid)
                # set GeoJSON properties
                properties = OrderedDict()
                properties["s2_token"] = token
                properties["grid_level"] = grid_level
                properties["max_mean_values"] = max_mean
                feature["properties"] = properties
                #
                features.append(feature)

        return features

    def get_max_mean_values(self, queryset):
        target_list = TargetSpecies.objects.values_list("species_id", flat=True)
        # set up data structure to store results
        concentration_values = []
        max_mean_values = []

        for species in target_list:
            concentration_dict = {"species": species, "values": []}
            concentration_values.append(concentration_dict)

        for bin in queryset:
            if bin.cell_concentration_data:
                for datapoint in bin.cell_concentration_data:
                    item = next(
                        (
                            item
                            for item in concentration_values
                            if item["species"] == datapoint["species"]
                        ),
                        None,
                    )

                    if item is not None:
                        item["values"].append(int(datapoint["cell_concentration"]))

        for item in concentration_values:
            if item["values"]:
                max_value = max(item["values"])
                mean_value = mean(item["values"])
            else:
                max_value = 0
                mean_value = 0

            data_dict = {
                "species": item["species"],
                "max_value": max_value,
                "mean_value": mean_value,
            }
            max_mean_values.append(data_dict)

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
        features = []
        grid_level = self.context["request"].query_params.get("grid_level", 0.5)

        try:
            grid_level = float(grid_level)
        except ValueError as e:
            grid_level = 0.4

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
        # print(square)
        target_list = TargetSpecies.objects.values_list("species_id", flat=True)
        index_list = [*range(0, target_list.count(), 1)]
        metrics = Metric.objects.filter(
            data_layer__belongs_to_app=DataLayer.IFCB_DATASETS
        )
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
                if str(i) in key:
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
