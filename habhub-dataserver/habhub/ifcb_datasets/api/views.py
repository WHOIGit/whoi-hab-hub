import datetime

from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.utils.timezone import make_aware
from django.db import models
from django.db.models import Prefetch, F, Q

from ..models import Dataset, Bin
from .serializers import DatasetListSerializer, DatasetDetailSerializer
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
    serializer_class = DatasetListSerializer
    detail_serializer_class = DatasetDetailSerializer

    def get_queryset(self):
        queryset = Dataset.objects.filter(fixed_location=False).defer("bins")
        # call custom filter method from mixin
        queryset = self.handle_query_param_filters(queryset)
        return queryset

    # return different sets of fields if the request is list all or retrieve one,
    # so use two different serializers
    def get_serializer_class(self):
        if self.action == "retrieve":
            if hasattr(self, "detail_serializer_class"):
                return self.detail_serializer_class

        return super(SpatialDatasetViewSet, self).get_serializer_class()
