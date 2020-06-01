from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import Station


class StationSerializer(GeoFeatureModelSerializer):
    toxicity_timeseries_data = serializers.SerializerMethodField('get_datapoints')
    station_max = serializers.SerializerMethodField('get_station_max')
    station_mean = serializers.SerializerMethodField('get_station_mean')

    class Meta:
        model = Station
        geo_field = 'geom'
        fields = ['id', 'station_name', 'state', 'station_location', 'geom', 'station_max', 'station_mean', 'toxicity_timeseries_data' ]

    def get_station_max(self, obj):
        dict = obj.get_max_mean_values()
        station_max = round(dict['station_max'])
        return station_max

    def get_station_mean(self, obj):
        dict = obj.get_max_mean_values()
        station_mean = round(dict['station_mean'])
        return station_mean

    def get_datapoints(self, obj):
        # Check if user wants to exclude datapoints
        exclude_dataseries = self.context.get('exclude_dataseries')
        if exclude_dataseries:
            return None

        # Otherwise create the datapoint series
        datapoints_qs = obj.datapoints.all()
        toxicity_timeseries_data = list()

        for datapoint in datapoints_qs:
            date_str = datapoint.measurement_date.strftime('%Y-%m-%d')
            toxicity_timeseries_data.append([date_str, float(datapoint.measurement)])

        return toxicity_timeseries_data

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary prefetching of data. """
        #queryset = queryset.select_related('location').select_related('part')
        queryset = queryset.prefetch_related('datapoints')
        return queryset
