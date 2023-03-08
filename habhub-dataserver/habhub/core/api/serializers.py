from rest_framework import serializers
from datetime import datetime, timedelta

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
    # start_date = serializers.SerializerMethodField("get_start_date")

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
            "max_mean",
            "active_features",
            "relative_date_range",
        )

    def to_representation(self, obj):
        rep = super().to_representation(obj)
        # need to change the start/end dates if this is a relative date range bookmark
        start_date = obj.start_date
        end_date = obj.end_date

        if obj.relative_date_range:
            print("Use relative date range: ", obj.relative_date_range)
            today = datetime.today()
            start_date = today - timedelta(days=obj.relative_date_range)
            end_date = today

        rep["start_date"] = start_date
        rep["end_date"] = end_date
        return rep


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
