from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import Dataset, SpeciesClassified


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
        for species in SpeciesClassified.TARGET_SPECIES:
            dict = {'species': species[1], 'data': [],}
            concentration_timeseries.append(dict)

        for bin in bins_qs:
            date_str = bin.sample_time.strftime('%Y-%m-%d')
            for datapoint in bin.species_classified.all():
                index = next((index for (index, dict) in enumerate(concentration_timeseries) if dict['species'] == datapoint.species), None)
                #dict = next((series for series in concentration_timeseries if series['species'] == datapoint.species), None)
                if index:
                    concentration_timeseries[index]['data'].append([date_str, float(datapoint.cell_concentration)])

        return concentration_timeseries

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary prefetching of data. """
        queryset = queryset.prefetch_related('bins__species_classified')
        return queryset
