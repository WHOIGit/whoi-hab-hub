import datetime

from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import models
from django.db.models import Prefetch, F, Q
from django.contrib.gis.db.models import Extent

from ..models import Dataset, Bin
from .serializers import (
    DatasetListSerializer, DatasetDetailSerializer, SpatialDatasetSerializer, SpatialBinSerializer, BoundingBoxSerializer,
    BinSerializer, SpatialGridSerializer
)
from .mixins import DatasetFiltersMixin, BinFiltersMixin

CACHE_TTL = 60 * 60


class BinViewSet(BinFiltersMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = BinSerializer

    def get_queryset(self):
        queryset = Bin.objects.filter(cell_concentration_data__isnull=False)
        # call custom filter method from mixin
        queryset = self.handle_query_param_filters(queryset)
        return queryset


class DatasetViewSet(DatasetFiltersMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = DatasetListSerializer
    detail_serializer_class = DatasetDetailSerializer

    @method_decorator(cache_page(CACHE_TTL))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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
        queryset = Dataset.objects.defer("bins")
        # call custom filter method from mixin
        queryset = self.handle_query_param_filters(queryset, is_fixed_location=False)
        return queryset


class SpatialBinViewSet(BinFiltersMixin, viewsets.ViewSet):
    def list(self, request):
        queryset = Bin.objects.filter(cell_concentration_data__isnull=False)
        queryset = self.handle_query_param_filters(queryset)
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


class SpatialGridViewSet(BinFiltersMixin, viewsets.ViewSet):
    def list(self, request):
        queryset = Bin.objects.filter(cell_concentration_data__isnull=False)
        queryset = self.handle_query_param_filters(queryset)
        serializer = SpatialGridSerializer(queryset, context={'request': request})
        return Response(serializer.data)
