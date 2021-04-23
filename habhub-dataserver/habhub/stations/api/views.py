import datetime

from rest_framework import generics, viewsets
from rest_framework.settings import api_settings
from rest_framework_csv.renderers import CSVRenderer
from django_filters import rest_framework as filters
from django.db import models
from django.utils.timezone import make_aware
from django.db.models import Prefetch, F, Avg, Max, Q

from ..models import Station, Datapoint
from .serializers import StationSerializer


class StationCSVRenderer(CSVRenderer):
    header = ["features.id", "features.geometry"]
    labels = {"features.id": "duck"}


class StationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ("station_name", "station_location")
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (CSVRenderer,)

    def get_queryset(self):
        queryset = Station.objects.all()
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        seasonal = self.request.query_params.get("seasonal", None) == "true"
        exclude_month_range = (
            self.request.query_params.get("exclude_month_range", None) == "true"
        )
        # integer to divide the total dataset bins by to smooth out long term graphs/improve performance
        smoothing_factor = int(self.request.query_params.get("smoothing_factor", 1))

        if start_date:
            start_date_obj = datetime.datetime.strptime(start_date, "%m/%d/%Y").date()
        if end_date:
            end_date_obj = datetime.datetime.strptime(end_date, "%m/%d/%Y").date()

        if start_date and end_date:
            # if "seaonsal" filter is True, need to get multiple date ranges across the time series
            date_q_filters = Q()
            if seasonal:
                date_ranges = []
                year_range = [*range(start_date_obj.year, end_date_obj.year + 1)]

                for year in year_range:
                    # if exclude_month_range filter is true, need to invert the date ranges so they span the next year
                    if exclude_month_range:
                        range_start_date = make_aware(
                            datetime.datetime(
                                year, end_date_obj.month, end_date_obj.day
                            )
                        )
                        range_end_date = make_aware(
                            datetime.datetime(
                                year + 1, start_date_obj.month, start_date_obj.day
                            )
                        )
                    else:
                        range_start_date = make_aware(
                            datetime.datetime(
                                year, start_date_obj.month, start_date_obj.day
                            )
                        )
                        range_end_date = make_aware(
                            datetime.datetime(
                                year, end_date_obj.month, end_date_obj.day
                            )
                        )

                    range_dict = {
                        "year": year,
                        "start_date": range_start_date,
                        "end_date": range_end_date,
                    }
                    date_ranges.append(range_dict)

                for dr in date_ranges:
                    date_q_filters |= Q(
                        measurement_date__range=(dr["start_date"], dr["end_date"])
                    )  # 'or' the Q objects together
            else:
                date_q_filters |= Q(
                    measurement_date__range=([start_date_obj, end_date_obj])
                )

            datapoint_query = Datapoint.objects.filter(date_q_filters)

            if smoothing_factor > 1:
                datapoint_query = datapoint_query.annotate(
                    smoothing=F("id") % smoothing_factor
                ).filter(smoothing=0)

            queryset = (
                queryset.prefetch_related(
                    Prefetch("datapoints", queryset=datapoint_query)
                )
                .add_station_max(date_q_filters)
                .add_station_mean(date_q_filters)
            )
        else:
            queryset = (
                queryset.prefetch_related("datapoints")
                .add_station_max()
                .add_station_mean()
            )
        return queryset
