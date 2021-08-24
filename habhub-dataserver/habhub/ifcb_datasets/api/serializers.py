from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

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
        concentration_timeseries = []

        # set up data structure to store results
        for species in TargetSpecies.objects.all():
            dict = {'species': species.species_id, 'species_display': species.display_name, 'data': [], }
            concentration_timeseries.append(dict)

        for bin in obj.bins.all():
            date_str = bin.sample_time.strftime('%Y-%m-%dT%H:%M:%SZ')

            for datapoint in bin.cell_concentration_data:
                index = next((index for (index, data) in enumerate(concentration_timeseries)
                             if data['species'] == datapoint['species']), None)

                if index is not None:
                    cell_concentration = 0
                    biovolume = 0

                    if 'cell_concentration' in datapoint:
                        cell_concentration = int(datapoint['cell_concentration'])

                    if 'biovolume' in datapoint:
                        biovolume = int(datapoint['biovolume'])

                    data_dict = {
                        'sample_time': date_str,
                        'bin_pid': bin.pid,
                        'data': [
                            {'metric_name': 'cell_concentration', 'value': cell_concentration},
                            {'metric_name': 'biovolume', 'value': biovolume}
                        ]
                    }
                    concentration_timeseries[index]['data'].append(data_dict)

        return concentration_timeseries
