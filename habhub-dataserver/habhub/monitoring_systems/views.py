from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core.serializers import serialize
from django.views.generic import View, DetailView, ListView, TemplateView

from .models import *

# Create your views here.

class MonitoringSystemMapUS(TemplateView):
    template_name = 'monitoring_systems/us_map.html'
    context_object_name = 'monitoring_systems'


# AJAX views to get GeoJSON responses for maps
class MonitoringSystemAjaxGetAllView(View):

    def get(self, request, *args, **kwargs):
        # Use GeoDjango geojson serializer to return JSON to map
        ms_json = serialize('geojson', MonitoringSystem.objects.all())
        return HttpResponse(ms_json, content_type='json')


class MonitoringSystemAjaxGetMonitoringView(View):

    def get(self, request, *args, **kwargs):
        # Use GeoDjango geojson serializer to return JSON to map
        ms_json = serialize('geojson', MonitoringSystem.objects.filter(system_type__icontains='Monitoring'))
        return HttpResponse(ms_json, content_type='json')


class MonitoringSystemAjaxGetForecastingView(View):

    def get(self, request, *args, **kwargs):
        # Use GeoDjango geojson serializer to return JSON to map
        ms_json = serialize('geojson', MonitoringSystem.objects.filter(system_type__icontains='Forecasting'))
        return HttpResponse(ms_json, content_type='json')
