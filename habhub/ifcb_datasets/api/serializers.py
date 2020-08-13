from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import Dataset, Bin


class DatasetSerializer(GeoFeatureModelSerializer):
    concentration_timeseries = serializers.SerializerMethodField('get_datapoints')

    class Meta:
        model = Dataset
        geo_field = 'geom'
        fields = ['id', 'name', 'location', 'dashboard_id_name', 'geom', 'concentration_timeseries' ]

    def get_datapoints(self, obj):
        # Check if user wants to exclude datapoints
        exclude_dataseries = self.context.get('exclude_dataseries')
        if exclude_dataseries:
            return None

        # Otherwise create the datapoint series
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
