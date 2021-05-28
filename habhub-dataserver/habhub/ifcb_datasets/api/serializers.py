import s2sphere
import math

from django.contrib.gis.db.models import Extent
from django.contrib.gis.geos import Polygon, Point
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField

from ..models import Dataset, Bin
from habhub.core.models import TargetSpecies


class DatasetListSerializer(GeoFeatureModelSerializer):
    max_mean_values = serializers.SerializerMethodField('get_max_mean_values')

    class Meta:
        model = Dataset
        geo_field = 'geom'
        fields = ['id', 'name', 'location', 'dashboard_id_name', 'geom', 'max_mean_values', ]

    def get_max_mean_values(self, obj):
        return obj.get_max_mean_values()


class DatasetDetailSerializer(DatasetListSerializer):
    timeseries_data = serializers.SerializerMethodField('get_datapoints')

    class Meta(DatasetListSerializer.Meta):
        fields = DatasetListSerializer.Meta.fields + ['timeseries_data', ]

    def __init__(self, *args, **kwargs):
        super(DatasetDetailSerializer, self).__init__(*args, **kwargs)

        if 'context' in kwargs:
            if 'request' in kwargs['context']:
                exclude_dataseries = kwargs['context']['request'].query_params.get('exclude_dataseries', None)
                if exclude_dataseries:
                    self.fields.pop('timeseries_data')

    def get_datapoints(self, obj):
        bins_qs = obj.bins.all()
        concentration_timeseries = list()

        # set up data structure to store results
        for species in TargetSpecies.objects.all():
            dict = {'species': species.species_id, 'species_display': species.display_name, 'data': [], }
            concentration_timeseries.append(dict)

        for bin in bins_qs:
            date_str = bin.sample_time.strftime('%Y-%m-%dT%H:%M:%SZ')

            for datapoint in bin.cell_concentration_data:
                index = next((index for (index, data) in enumerate(concentration_timeseries)
                             if data['species'] == datapoint['species']), None)
                if index is not None:
                    data_dict = {
                        'sample_time': date_str,
                        'cell_concentration': int(datapoint['cell_concentration']),
                        'bin_pid': bin.pid,
                    }
                    concentration_timeseries[index]['data'].append(data_dict)

        return concentration_timeseries


class SpatialDatasetSerializer(serializers.ModelSerializer):
    timeseries_data = serializers.SerializerMethodField('get_datapoints')
    max_mean_values = serializers.SerializerMethodField('get_max_mean_values')
    #bbox = GeometrySerializerMethodField()
    grid_center_points = serializers.SerializerMethodField('get_grid_center_points')

    class Meta:
        model = Dataset
        fields = ['id', 'name', 'location', 'dashboard_id_name', 'grid_center_points', 'max_mean_values', 'timeseries_data' ]

    def convert_s2_point_to_latlng(self, s2_point):
        coords = str(s2_point).split()[-1].split(",")
        lat_lng = {"lat": float(coords[0]), "long": float(coords[1])}
        return lat_lng

    def get_grid_center_points(self, obj):
        zero_pt = Point(0, 0)
        #dp = obj.bins.latest()
        qs = obj.bins.filter(geom__isnull=False).exclude(geom=zero_pt).aggregate(Extent('geom'))
        print(qs['geom__extent'])

        # S2 functions to get gridded
        r = s2sphere.RegionCoverer()
        r.min_level=7
        r.max_level=7
        p1 = s2sphere.LatLng.from_degrees(qs['geom__extent'][1], qs['geom__extent'][0])
        p2 = s2sphere.LatLng.from_degrees(qs['geom__extent'][3], qs['geom__extent'][2])
        #box = s2sphere.LatLngRect.from_point_pair(p1, p2)
        #print(box)
        covering = r.get_covering(s2sphere.LatLngRect.from_point_pair(p1, p2))
        points = []
        for cellid in covering:
            cell = s2sphere.Cell(cellid)
            cell_center_point = cell.get_center()
            cell_center_ll = s2sphere.LatLng.from_point(cell_center_point)
            lat_lng = self.convert_s2_point_to_latlng(cell_center_ll)
            points.append(lat_lng)

        return points
        #print(lat_lng)

        """
        # Builds GEOS polygons out of cell vertices
        vertices = []
        print(new_cell.get_rect_bound())
        vertices = [s2sphere.LatLng.from_point(s2sphere.Cell(cellid).get_vertex(v)) for v in range(4)]
        print(len(vertices))
        points = []
        for v in vertices:
            # get just lat/long coords from S2 LatLng
            print(v.lat())
            coords = str(v).split()[-1].split(",")
            print(coords)
            point = Point(float(coords[1]), float(coords[0]))
            print(point)
            points.append(point)
        # close the loop for a Polygon
        points.append(points[0])
        print(points)
        poly = Polygon(points)
        print(poly)
        geoms.append(poly)
        """

    def get_max_mean_values(self, obj):
        return obj.get_max_mean_values()

    def get_datapoints(self, obj):
        bins_qs = obj.bins.all()
        concentration_timeseries = list()

        # set up data structure to store results
        for species in TargetSpecies.objects.all():
            dict = {'species': species.species_id, 'species_display': species.display_name, 'data': [], }
            concentration_timeseries.append(dict)

        for bin in bins_qs:
            date_str = bin.sample_time.strftime('%Y-%m-%dT%H:%M:%SZ')

            for datapoint in bin.cell_concentration_data:
                index = next((index for (index, data) in enumerate(concentration_timeseries)
                             if data['species'] == datapoint['species']), None)
                if index is not None:
                    data_dict = {
                        'sample_time': date_str,
                        'cell_concentration': int(datapoint['cell_concentration']),
                        'bin_pid': bin.pid,
                    }
                    concentration_timeseries[index]['data'].append(data_dict)

        return concentration_timeseries
