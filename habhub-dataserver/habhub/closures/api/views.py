import datetime

from rest_framework import generics, viewsets
from django_filters import rest_framework as filters
from django.utils import timezone
from django.utils.timezone import make_aware
from django.db import models
from django.db.models import Prefetch, F, Q

from ..models import (
    ClosureNotice,
    ClosureDataEvent,
    ShellfishArea,
)
from .serializers import ClosureDataEventSerializer, ShellfishAreaSerializer


class ClosureDataEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ClosureDataEventSerializer
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):
        queryset = ClosureDataEvent.objects.all()
        return queryset


class ShellfishAreaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShellfishAreaSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ["state"]

    def get_queryset(self):
        queryset = ShellfishArea.objects.all()
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        state = self.request.query_params.get("state", None)
        seasonal = self.request.query_params.get('seasonal', None) == 'true'
        exclude_month_range = self.request.query_params.get('exclude_month_range', None) == 'true'
        earliest_closure = ClosureNotice.objects.earliest()

        if start_date:
            start_date_obj = datetime.datetime.strptime(start_date, "%m/%d/%Y").date()
        else:
            start_date_obj = earliest_closure.effective_date

        if end_date:
            end_date_obj = datetime.datetime.strptime(end_date, "%m/%d/%Y").date()
        else:
            end_date_obj = timezone.now()

        if start_date or end_date:
            date_q_filters = Q()

            if seasonal:
                date_ranges = []
                year_range = [*range(start_date_obj.year, end_date_obj.year+1)]

                for year in year_range:
                    # if exclude_month_range filter is true, need to invert the date ranges so they span the next year
                    if exclude_month_range:
                        range_start_date = make_aware(datetime.datetime(year, end_date_obj.month , end_date_obj.day))
                        range_end_date = make_aware(datetime.datetime(year + 1, start_date_obj.month, start_date_obj.day))
                    else:
                        range_start_date = make_aware(datetime.datetime(year, start_date_obj.month, start_date_obj.day))
                        range_end_date = make_aware(datetime.datetime(year, end_date_obj.month, end_date_obj.day))

                    range_dict = {
                        'year': year,
                        'start_date': range_start_date,
                        'end_date': range_end_date
                    }
                    date_ranges.append(range_dict)

                for dr in date_ranges:
                    date_q_filters |= Q(effective_date__range=(dr['start_date'], dr['end_date'])) # 'or' the Q objects together
            else:
                date_q_filters |= Q(effective_date__range=(start_date_obj, end_date_obj))

            # get initial list of notice IDs to only return Shellfish Areas with Closures
            notice_date_ids = ClosureNotice.objects.filter(date_q_filters).filter(notice_action="Closed").values("id")

            queryset = queryset.filter(closure_notices__in=notice_date_ids).distinct()

            # create subquery to also filter the ClosureNotice set that is prefetched
            closure_notice_query = ClosureNotice.objects.filter(date_q_filters).filter(notice_action="Closed")

            # do the prefetching
            queryset = queryset.prefetch_related(
                Prefetch("closure_notices", queryset=closure_notice_query)
            )

        else:
            queryset = queryset.exclude(closure_notices=None).prefetch_related(
                "closure_notices"
            )
        return queryset
