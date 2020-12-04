from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import Dataset, Bin


class DatasetSerializer(GeoFeatureModelSerializer):
    concentration_timeseries = serializers.SerializerMethodField('get_datapoints')
    max_mean_values = serializers.SerializerMethodField('get_max_mean_values')

    class Meta:
        model = Dataset
        geo_field = 'geom'
        fields = ['id', 'name', 'location', 'dashboard_id_name', 'geom', 'max_mean_values', 'concentration_timeseries', ]

    def __init__(self, *args, **kwargs):
        super(DatasetSerializer, self).__init__(*args, **kwargs)

        if 'context' in kwargs:
            if 'request' in kwargs['context']:
                exclude_dataseries = kwargs['context']['request'].query_params.get('exclude_dataseries', None)
                if exclude_dataseries:
                    self.fields.pop('concentration_timeseries')

    def get_max_mean_values(self, obj):
        return obj.get_max_mean_values()

    def get_datapoints(self, obj):
        bins_qs = obj.bins.all()
        concentration_timeseries = list()

        # set up data structure to store results
        for species in Bin.TARGET_SPECIES:
            dict = {'species': species[0], 'species_display': species[1], 'data': [],}
            concentration_timeseries.append(dict)

        for bin in bins_qs:
            if bin.cell_concentration_data:
                date_str = bin.sample_time.strftime('%Y-%m-%dT%H:%M:%SZ')

                for datapoint in bin.cell_concentration_data:
                    index = next((index for (index, d) in enumerate(concentration_timeseries) if d['species'] == datapoint['species']), None)
                    if index is not None:
                        data_dict = {
                            'sample_time': date_str,
                            'cell_concentration': int(datapoint['cell_concentration']),
                            'bin_pid': bin.pid,
                        }
                        concentration_timeseries[index]['data'].append(data_dict)
                        #concentration_timeseries[index]['data'].append([date_str, int(datapoint['cell_concentration'])])

        return concentration_timeseries

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary prefetching of data. """
        queryset = queryset.prefetch_related('bins')
        return queryset
