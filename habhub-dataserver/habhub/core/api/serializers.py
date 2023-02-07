from rest_framework import serializers

from ..models import MapBookmark, TargetSpecies, DataLayer
from habhub.stations.models import Datapoint
from habhub.ifcb_datasets.models import Bin
from habhub.closures.models import ClosureNotice


class TargetSpeciesSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="species_id")

    class Meta:
        model = TargetSpecies
        fields = (
            "id",
            "display_name",
            "syndrome",
            "primary_color",
            "color_gradient",
            "species_environment",
            "species_type",
        )


class DataLayerSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="layer_id")

    class Meta:
        model = DataLayer
        fields = ("id", "name")


class MapBookmarkSerializer(serializers.ModelSerializer):
    species = serializers.ListField(child=serializers.CharField())
    data_layers = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = MapBookmark
        fields = (
            "id",
            "start_date",
            "end_date",
            "species",
            "data_layers",
            "latitude",
            "longitude",
            "zoom",
            "seasonal",
            "exclude_month_range",
        )


class DatapointSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField()
    data_count = serializers.IntegerField()
    density_percentage = serializers.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        model = Datapoint
        fields = (
            "timestamp",
            "data_count",
            "density_percentage",
        )


class BinSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField()
    data_count = serializers.IntegerField()
    density_percentage = serializers.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        model = Bin
        fields = (
            "timestamp",
            "data_count",
            "density_percentage",
        )


class ClosureNoticeSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateField()
    data_count = serializers.IntegerField()
    density_percentage = serializers.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        model = ClosureNotice
        fields = (
            "timestamp",
            "data_count",
            "density_percentage",
        )
