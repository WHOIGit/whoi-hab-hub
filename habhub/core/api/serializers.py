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
            'timestamp', 'count',
        )


class BinSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField()
    count = serializers.IntegerField()

    class Meta:
        model = Bin
        fields = (
            'timestamp', 'count',
        )


class ClosureNoticeSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateField()
    count = serializers.IntegerField()

    class Meta:
        model = ClosureNotice
        fields = (
            'timestamp', 'count',
        )
