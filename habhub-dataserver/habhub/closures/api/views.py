import datetime
from dateutil.relativedelta import relativedelta
from rest_framework import generics, viewsets
from django_filters import rest_framework as filters
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import models
from django.db.models import Prefetch, F, Q

from ..models import (
    ClosureNotice,
    ShellfishArea,
)
from .serializers import ShellfishAreaListSerializer, ShellfishAreaDetailSerializer
from .mixins import ShellfishAreaMixin

CACHE_TTL = 60 * 60


class ShellfishAreaViewSet(ShellfishAreaMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ShellfishAreaListSerializer
    detail_serializer_class = ShellfishAreaDetailSerializer
    # filter_backends = (filters.DjangoFilterBackend,)
    # filterset_fields = ["state"]

    @method_decorator(cache_page(CACHE_TTL))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    # return different sets of fields if the request is list all or retrieve one,
    # so use two different serializers
    def get_serializer_class(self):
        print(self.action)
        if self.action == "retrieve":
            if hasattr(self, "detail_serializer_class"):
                return self.detail_serializer_class

        return super(ShellfishAreaViewSet, self).get_serializer_class()

    def get_queryset(self):
        queryset = ShellfishArea.objects.all()
        queryset = self.handle_query_param_filters(queryset)
        return queryset


class ShellfishAreaAllDataViewSet(ShellfishAreaMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ShellfishAreaDetailSerializer

    @method_decorator(cache_page(CACHE_TTL))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = ShellfishArea.objects.all()
        queryset = self.handle_query_param_filters(queryset)
        return queryset
