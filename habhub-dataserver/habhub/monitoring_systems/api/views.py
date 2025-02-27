from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from ..models import MonitoringSystem
from .serializers import MonitoringSystemSerializer, ForecastingSystemSerializer


class MonitoringSystemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonitoringSystem.objects.filter(system_type__icontains="Monitoring")
    serializer_class = MonitoringSystemSerializer


class ForecastingSystemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonitoringSystem.objects.filter(system_type__icontains="Forecasting")
    serializer_class = ForecastingSystemSerializer
