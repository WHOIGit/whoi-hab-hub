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
        fields = [
            'id', 'station_name', 'state', 'station_location', 'geom', 'station_max', 'station_mean', 'hab_species', 'toxicity_timeseries_data'
        ]

    def get_station_max(self, obj):
        dict = obj.get_max_mean_values()
        if dict['station_max']:
            station_max = float(round(dict['station_max'], 1))
            return station_max
        return 0

    def get_station_mean(self, obj):
        dict = obj.get_max_mean_values()
        if dict['station_mean']:
            station_mean = float(round(dict['station_mean'], 1))
            return station_mean
        return 0

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

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary prefetching of data. """
        #queryset = queryset.select_related('location').select_related('part')
        queryset = queryset.prefetch_related('datapoints')
        return queryset
