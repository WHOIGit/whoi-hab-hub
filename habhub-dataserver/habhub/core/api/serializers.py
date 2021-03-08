from rest_framework import serializers

from habhub.stations.models import Datapoint
from habhub.ifcb_datasets.models import Bin
from habhub.closures.models import ClosureNotice


class DatapointSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField()
    count = serializers.IntegerField()

    class Meta:
        model = Datapoint
        fields = (
            'timestamp',
            'count',
            #'density_percentage',
        )


class BinSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField()
    count = serializers.IntegerField()

    class Meta:
        model = Bin
        fields = (
            'timestamp',
            'count',
            #'density_percentage',
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
