from rest_framework import serializers
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer, GeometrySerializerMethodField
)

from ..models import ClosureNotice, ClosureDataEvent, ShellfishArea


class ShellfishAreaSerializer(GeoFeatureModelSerializer):
    simplified_geom = GeometrySerializerMethodField()
    closures = serializers.SerializerMethodField()

    class Meta:
        model = ShellfishArea
        geo_field = 'simplified_geom'
        fields = ('id', 'name', 'state', 'acres', 'area_description', 'closures', 'simplified_geom',)

    def get_simplified_geom(self, obj):
        # Returns a new GEOSGeometry, simplified to the specified tolerance
        # using the Douglas-Peucker algorithm. A higher tolerance value implies
        # fewer points in the output. If no tolerance is provided, it
        # defaults to 0.
        return obj.geom.simplify(tolerance=0.001, preserve_topology=True)

    def get_closures(self, obj):
        if obj.closure_notices.exists():
            closures = obj.closure_notices.all()
        else:
            return None

        closures_list = []
        for closure in closures:
            if closure.causative_organism:
                causative_organism = closure.causative_organism.name
            else:
                causative_organism = 'Unknown'

            data = {
                "title":  closure.title,
                "id":  closure.id,
                "year": closure.effective_date.year,
                "month": closure.effective_date.month,
                "species": [species.name for species in closure.species.all()],
                "causative_organism": causative_organism,
                "effective_date" : closure.effective_date,
            }
            closures_list.append(data)
        return closures_list


class ClosureDataEventSerializer(GeoFeatureModelSerializer):
    geom = GeometrySerializerMethodField('get_shellfish_area_geom')

    class Meta:
        model = ClosureDataEvent
        geo_field = 'geom'
        fields = ('id', 'closure_notice', 'species', 'effective_date', 'notice_action', 'duration', 'causative_organism', 'geom',)

    def get_shellfish_area_geom(self, obj):
        return obj.shellfish_area.geom.simplify(tolerance=0.0001, preserve_topology=True)
