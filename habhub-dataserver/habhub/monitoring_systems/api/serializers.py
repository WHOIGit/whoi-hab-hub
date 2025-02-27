from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
)

from ..models import MonitoringSystem


class MonitoringSystemSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = MonitoringSystem
        geo_field = "geom"
        fields = [
            "id",
            "name",
            "description",
            "system_type",
            "geom",
            "url",
            "location",
            "alt_url",
            "alt_location",
            "latitude",
            "longitude",
        ]


class ForecastingSystemSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = MonitoringSystem
        geo_field = "geom"
        fields = [
            "id",
            "name",
            "description",
            "system_type",
            "geom",
            "url",
            "location",
            "alt_url",
            "alt_location",
            "latitude",
            "longitude",
        ]
