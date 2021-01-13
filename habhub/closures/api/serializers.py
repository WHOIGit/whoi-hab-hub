from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from ..models import ClosureNotice, ClosureDataEvent, ShellfishArea


class ShellfishAreaSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = ShellfishArea
        geo_field = 'geom'
        fields = ['id', 'name', 'state', 'acres', 'area_description', 'geom', ]


class ClosureDataEventSerializer(GeoFeatureModelSerializer):
    geom = serializers.SerializerMethodField('get_shellfish_area_geom')

    class Meta:
        model = ClosureDataEvent
        geo_field = 'geom'
        fields = ['id', 'closure_notice', 'species', 'effective_date', 'notice_action', 'duration', 'causative_organism', 'geom', ]

    def get_shellfish_area_geom(self, obj):
        return obj.shellfish_area.geom
