import datetime

from rest_framework import generics, viewsets
from django_filters import rest_framework as filters
from django.utils import timezone
from django.db import models
from django.db.models import Prefetch, F

from ..models import (
    ClosureNotice, ClosureDataEvent, ShellfishArea,
)
from .serializers import (
    ClosureDataEventSerializer,
    ShellfishAreaSerializer
)


class ClosureDataEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ClosureDataEventSerializer
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):
        queryset = ClosureDataEvent.objects.all()
        return queryset


class ShellfishAreaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShellfishAreaSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['state']

    def get_queryset(self):
        queryset = ShellfishArea.objects.all()
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        earliest_closure = ClosureNotice.objects.earliest()

        if start_date:
            start_date_obj = datetime.datetime.strptime(start_date, '%m/%d/%Y').date()
        else:
            start_date_obj = earliest_closure.effective_date

        if end_date:
            end_date_obj = datetime.datetime.strptime(end_date, '%m/%d/%Y').date()
        else:
            end_date_obj = timezone.now()

        if start_date or end_date:
            # get initial list of notice IDs to only return Shellfish Areas with Closures
            notice_date_ids = (
                ClosureNotice.objects.filter(effective_date__range=[start_date_obj, end_date_obj], notice_action='Open')
                                     .values('id')
            )
            queryset = queryset.filter(closure_notices__in=notice_date_ids).distinct()
            # create subquery to also filter the ClosureNotice set that is prefetched
            closure_notice_query = ClosureNotice.objects.filter(effective_date__range=[start_date_obj, end_date_obj], notice_action='Open')
            # do the prefetching
            queryset = queryset.prefetch_related(
                Prefetch(
                    'closure_notices',
                    queryset=closure_notice_query
                ))

        else:
            queryset = (
                queryset.exclude(closure_notices=None).prefetch_related('closure_notices')
            )
        return queryset
