import datetime

from rest_framework import generics, viewsets
from django_filters import rest_framework as filters
from django.utils import timezone
from django.db import models
from django.db.models import Prefetch, F

from ..models import ClosureDataEvent, ShellfishArea
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
    filterset_fields = ['state']

    def get_queryset(self):
        queryset = ShellfishArea.objects.all()
        return queryset
