import environ

from rest_framework import viewsets
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
    DatasetListSerializer,
    DatasetDetailSerializer,
    BinSerializer,
    BinSpatialGridSerializer,
    BinSpatialGridDetailSerializer,
)
from .mixins import DatasetFiltersMixin, BinFiltersMixin

env = environ.Env()

CACHE_TTL = env("CACHE_TTL", default=60 * 60)


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


class BinSpatialGridViewSet(BinFiltersMixin, viewsets.ViewSet):
    # @method_decorator(cache_page(CACHE_TTL))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def list(self, request):
        queryset = Bin.objects.filter(
            cell_concentration_data__isnull=False, geom__isnull=False
        )
        queryset = self.handle_query_param_filters(queryset)
        serializer = BinSpatialGridSerializer(queryset, context={"request": request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        # use the unique Geohash for the pk lookup
        print(pk)
        queryset = Bin.objects.filter(
            cell_concentration_data__isnull=False, geom__isnull=False
        )
        queryset = self.handle_query_param_filters(queryset)

        serializer = BinSpatialGridDetailSerializer(
            queryset, context={"request": request, "geohash": pk}
        )
        return Response(serializer.data)
