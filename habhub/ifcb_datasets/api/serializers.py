from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import Dataset, Bin, SpeciesClassified


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
            dict = {'species': species[0], 'data': [],}
            concentration_timeseries.append(dict)

        for bin in bins_qs:
            if bin.cell_concentration_data:
                date_str = bin.sample_time.strftime('%Y-%m-%d %H:%M:%S')

                for datapoint in bin.cell_concentration_data:
                    index = int(next((index for (index, d) in enumerate(concentration_timeseries) if d['species'] == datapoint['species']), None))
                    if index is not None:
                        concentration_timeseries[index]['data'].append([date_str, int(datapoint['cell_concentration'])])

        return concentration_timeseries

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary prefetching of data. """
        queryset = queryset.prefetch_related('bins')
        return queryset
