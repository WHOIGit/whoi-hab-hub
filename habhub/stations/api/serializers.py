from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import Station


class StationSerializer(GeoFeatureModelSerializer):
    toxicity_timeseries_data = serializers.SerializerMethodField('get_datapoints')

    class Meta:
        model = Station
        geo_field = 'geom'
        fields = ['id', 'station_name', 'state', 'station_location', 'geom', 'toxicity_timeseries_data' ]

    def get_datapoints(self, obj):
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
