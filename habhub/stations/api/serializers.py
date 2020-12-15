from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import Station


class StationSerializer(GeoFeatureModelSerializer):
    toxicity_timeseries_data = serializers.SerializerMethodField('get_datapoints')
    max_mean_values = serializers.SerializerMethodField('get_max_mean_values')

    class Meta:
        model = Station
        geo_field = 'geom'
        fields = [
            'id', 'station_name', 'state', 'station_location', 'geom', 'max_mean_values', 'hab_species', 'toxicity_timeseries_data'
        ]

    def get_max_mean_values(self, obj):
        return obj.get_max_mean_values()

    def get_datapoints(self, obj):
        # Check if user wants to exclude datapoints
        exclude_dataseries = self.context.get('exclude_dataseries')
        if exclude_dataseries:
            return None

        # Otherwise create the datapoint series
        datapoints_qs = obj.datapoints.all()
        toxicity_timeseries_data = list()

        for datapoint in datapoints_qs:
            date_str = datapoint.measurement_date.isoformat()
            data_obj = {'date': date_str, 'measurement': float(datapoint.measurement)}
            toxicity_timeseries_data.append(data_obj)

        return toxicity_timeseries_data
