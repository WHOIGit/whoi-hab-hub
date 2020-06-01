import datetime

from rest_framework import generics, viewsets
from django_filters import rest_framework as filters
from django.db import models
from django.db.models import Prefetch

from ..models import Station, Datapoint
from .serializers import StationSerializer


class StationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('station_name', 'station_location')

    def get_queryset(self):
        queryset = Station.objects.all()
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date:
            start_date_obj = datetime.datetime.strptime(start_date, '%m/%d/%Y').date()
        if end_date:
            end_date_obj = datetime.datetime.strptime(end_date, '%m/%d/%Y').date()

        if start_date and end_date:
            queryset = queryset.prefetch_related(Prefetch(
                'datapoints',
                queryset=Datapoint.objects.filter(measurement_date__range=[start_date_obj, end_date_obj])))
        # Set up eager loading to avoid N+1 selects
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset
