import datetime

from rest_framework import generics, viewsets
from django_filters import rest_framework as filters
from django.utils import timezone
from django.db import models
from django.db.models import Prefetch

from ..models import Dataset, Bin
from .serializers import DatasetSerializer


class DatasetViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DatasetSerializer
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):
        queryset = Dataset.objects.exclude(dashboard_id_name='mvco')
        earliest_bin = Bin.objects.earliest()
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date:
            start_date_obj = datetime.datetime.strptime(start_date, '%m/%d/%Y').date()
        else:
            start_date_obj = earliest_bin.sample_time

        if end_date:
            end_date_obj = datetime.datetime.strptime(end_date, '%m/%d/%Y').date()
        else:
            end_date_obj = timezone.now()

        if start_date or end_date:
            queryset = queryset.prefetch_related(Prefetch(
                'bins',
                queryset=Bin.objects.filter(sample_time__range=[start_date_obj, end_date_obj])))
            return queryset
        # Set up eager loading to avoid N+1 selects
        #queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset
