from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import Station


class StationSerializer(GeoFeatureModelSerializer):
    timeseries_data = serializers.SerializerMethodField('get_datapoints')
    max_mean_values = serializers.SerializerMethodField('get_max_mean_values')

    class Meta:
        model = Station
        geo_field = 'geom'
        fields = [
            'id', 'station_name', 'state', 'station_location', 'geom', 'max_mean_values', 'hab_species', 'timeseries_data'
        ]

    def get_max_mean_values(self, obj):
        max_mean_values = []

        if obj.station_max:
            data_dict = {
                'species': 'Alexandrium_catenella',
                'max_value': float(round(obj.station_max, 1)),
                'mean_value': float(round(obj.station_mean, 1)),
            }
            max_mean_values.append(data_dict)
        return max_mean_values

    def get_datapoints(self, obj):
        # Check if user wants to exclude datapoints
        exclude_dataseries = self.context.get('exclude_dataseries')
        if exclude_dataseries:
            return None

        # Otherwise create the datapoint series
        datapoints_qs = obj.datapoints.all()
        timeseries_data = list()

        for datapoint in datapoints_qs:
            date_str = datapoint.measurement_date.isoformat()
            data_obj = {'date': date_str, 'measurement': float(datapoint.measurement)}
            timeseries_data.append(data_obj)

        return timeseries_data
