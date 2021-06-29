import datetime

from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.utils.timezone import make_aware
from django.db import models
from django.db.models import Prefetch, F, Q
from django.contrib.gis.geos import Polygon
from django.contrib.gis.db.models import Extent

from ..models import Dataset, Bin
from .serializers import DatasetListSerializer, DatasetDetailSerializer, SpatialDatasetSerializer, SpatialBinSerializer, BoundingBoxSerializer
from .mixins import DatasetFiltersMixin


class DatasetViewSet(DatasetFiltersMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = DatasetListSerializer
    detail_serializer_class = DatasetDetailSerializer

    def get_queryset(self):
        queryset = Dataset.objects.filter(fixed_location=True).defer("bins")
        # call custom filter method from mixin
        queryset = self.handle_query_param_filters(queryset)
        return queryset

    # return different sets of fields if the request is list all or retrieve one,
    # so use two different serializers
    def get_serializer_class(self):
        if self.action == "retrieve":
            if hasattr(self, "detail_serializer_class"):
                return self.detail_serializer_class

        return super(DatasetViewSet, self).get_serializer_class()


class SpatialDatasetViewSet(DatasetFiltersMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = SpatialDatasetSerializer

    def get_queryset(self):
        queryset = Dataset.objects.filter(fixed_location=False).defer("bins")
        # call custom filter method from mixin
        queryset = self.handle_query_param_filters(queryset, is_fixed_location=False)
        return queryset


class SpatialBinViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = self.handle_query_param_filters()
        serializer = SpatialBinSerializer(queryset, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, url_path="max-bounding-box")
    def max_bounding_box(self, request):
        # Get the maximum size bounding box that can be returned from queryset
        # Extent returns (ne, sw) points of box
        bbbox_extent = Bin.objects.all().aggregate(Extent('geom'))
        print(bbbox_extent)
        bounding_box = bbbox_extent["geom__extent"]
        data = {"bounding_box": bounding_box}
        #poly = Polygon.from_bbox(bbox)
        serializer = BoundingBoxSerializer(data)
        return Response(serializer.data)

    def handle_query_param_filters(self):
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        seasonal = self.request.query_params.get("seasonal", None) == "true"
        exclude_month_range = (
            self.request.query_params.get("exclude_month_range", None) == "true"
        )
        # integer to divide the total dataset bins by to smooth out long term graphs/improve performance
        smoothing_factor = self.request.query_params.get("smoothing_factor", 1)
        bbox_sw = self.request.query_params.get("bbox_sw", None)
        bbox_ne = self.request.query_params.get("bbox_ne", None)

        try:
            earliest_bin = Bin.objects.earliest()
        except Bin.DoesNotExist:
            return queryset

        if start_date:
            start_date_obj = datetime.datetime.strptime(start_date, "%m/%d/%Y").date()
        else:
            start_date_obj = earliest_bin.sample_time

        if end_date:
            end_date_obj = datetime.datetime.strptime(end_date, "%m/%d/%Y").date()
        else:
            end_date_obj = timezone.now()

        # create empty Q objects to handle conditional filtering
        date_q_filters = Q()

        if start_date or end_date:
            # if "seaonsal" filter is True, need to get multiple date ranges across the time series
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
                        sample_time__range=(dr["start_date"], dr["end_date"])
                    )  # 'or' the Q objects together
            else:
                date_q_filters |= Q(
                    sample_time__range=([start_date_obj, end_date_obj])
                )

        queryset = (
            Bin.objects.filter(
            cell_concentration_data__isnull=False
            )
            .filter(date_q_filters)
            .annotate(smoothing=F("id") % smoothing_factor)
            .filter(smoothing=0)
        )

        if bbox_sw and bbox_ne:
            bbox_sw = bbox_sw.split(",")
            bbox_ne = bbox_ne.split(",")
            poly_bbox = Polygon.from_bbox(bbox_sw + bbox_ne)
            print(poly_bbox)
            queryset = queryset.filter(geom__within=poly_bbox)

        return queryset
