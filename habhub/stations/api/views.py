from rest_framework import generics, viewsets, filters
from ..models import Station
from .serializers import StationSerializer


class StationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StationSerializer
    search_fields = ['station_name']
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        queryset = Station.objects.all().get_max_mean_values()
        # Set up eager loading to avoid N+1 selects
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset
