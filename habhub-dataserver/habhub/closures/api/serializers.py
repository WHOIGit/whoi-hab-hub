from rest_framework import serializers
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeometrySerializerMethodField,
)

from ..models import ClosureNotice, ClosureDataEvent, ShellfishArea


class ShellfishAreaListSerializer(GeoFeatureModelSerializer):
    simplified_geom = GeometrySerializerMethodField()

    class Meta:
        model = ShellfishArea
        geo_field = "simplified_geom"
        fields = [
            "id",
            "name",
            "state",
            "acres",
            "area_description",
            "geom_center_point",
            "simplified_geom",
        ]

    def get_simplified_geom(self, obj):
        # Returns a new GEOSGeometry, simplified to the specified tolerance
        # using the Douglas-Peucker algorithm. A higher tolerance value implies
        # fewer points in the output. If no tolerance is provided, it
        # defaults to 0.
        return obj.geom.simplify(tolerance=0.001, preserve_topology=True)


class ShellfishAreaDetailSerializer(ShellfishAreaListSerializer):
    closures = serializers.SerializerMethodField()

    class Meta(ShellfishAreaListSerializer.Meta):
        fields = ShellfishAreaListSerializer.Meta.fields + ['closures',]

    def get_closures(self, obj):
        if obj.closure_notices.exists():
            closures_qs = obj.closure_notices.all()
        else:
            return None

        closures_list = []
        for closure in closures_qs:
            if closure.causative_organism:
                causative_organism = closure.causative_organism.name
            else:
                causative_organism = "Unknown"

            document_url = None
            if closure.document:
                document_url = closure.document.url

            species_list = []
            data_events_qs = (
                closure.closure_data_events
                .filter(shellfish_area=obj)
                .prefetch_related('species')
            )

            for event in data_events_qs:
                event_data = {"species": event.species.name, "duration": event.get_closure_duration}
                species_list.append(event_data)

            data = {
                "title": closure.title,
                "id": closure.id,
                "year": closure.effective_date.year,
                "month": closure.effective_date.month,
                "species": species_list,
                "causative_organism": causative_organism,
                "effective_date": closure.effective_date,
                "document_link": document_url,
            }
            closures_list.append(data)
        return closures_list
