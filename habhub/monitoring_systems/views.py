from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View, DetailView, ListView, TemplateView

from .models import *

# Create your views here.

class MonitoringSystemMapUS(TemplateView):
    template_name = 'monitoring_systems/us_map.html'
    context_object_name = 'monitoring_systems'
