from django.shortcuts import render
from django.views.generic import View, DetailView, ListView

from .models import Station, Datapoint

# Create your views here.
class StationListView(ListView):
    model = Station
    template_name = 'stations/station_list.html'
    context_object_name = 'stations'
