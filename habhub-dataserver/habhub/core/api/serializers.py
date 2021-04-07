from rest_framework import serializers

from ..models import TargetSpecies, DataLayer
from habhub.stations.models import Datapoint
from habhub.ifcb_datasets.models import Bin
from habhub.closures.models import ClosureNotice


class TargetSpeciesSerializer(serializers.ModelSerializer):

    class Meta:
        model = TargetSpecies
        fields = (
            'species_id',
            'display_name'
        )


class DataLayerSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='layer_id')

    class Meta:
        model = DataLayer
        fields = (
            'id',
            'name'
        )


class DatapointSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField()
    data_count = serializers.IntegerField()
    density_percentage = serializers.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        model = Datapoint
        fields = (
            'timestamp',
            'data_count',
            'density_percentage',
        )


class BinSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField()
    data_count = serializers.IntegerField()
    density_percentage = serializers.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        model = Bin
        fields = (
            'timestamp',
            'data_count',
            'density_percentage',
        )


class ClosureNoticeSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateField()
    data_count = serializers.IntegerField()
    density_percentage = serializers.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        model = ClosureNotice
        fields = (
            'timestamp',
            'data_count',
            'density_percentage',
        )
