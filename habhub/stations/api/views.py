import datetime

from rest_framework import generics, viewsets
from django_filters import rest_framework as filters
from django.db import models
from django.db.models import Prefetch, F, Avg, Max

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
        # integer to divide the total dataset bins by to smooth out long term graphs/improve performance
        smoothing_factor = self.request.query_params.get('smoothing_factor', 1)

        if start_date:
            start_date_obj = datetime.datetime.strptime(start_date, '%m/%d/%Y').date()
        if end_date:
            end_date_obj = datetime.datetime.strptime(end_date, '%m/%d/%Y').date()

        if start_date and end_date:
            queryset = queryset.prefetch_related(Prefetch(
                    'datapoints',
                    queryset=Datapoint.objects.filter(measurement_date__range=[start_date_obj, end_date_obj]) \
                    .annotate(smoothing=F('id') % smoothing_factor).filter(smoothing=0)
                )) \
                .add_station_max(start_date_obj, end_date_obj) \
                .add_station_mean(start_date_obj, end_date_obj)
        else:
            queryset = (
                queryset.prefetch_related('datapoints')
                        .add_station_max()
                        .add_station_mean()
            )
        return queryset
