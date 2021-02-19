from django.shortcuts import render
from django.views.generic import View, DetailView, ListView, TemplateView

# Create your views here.
class MapMainView(TemplateView):
    template_name = 'dashboard/map_main.html'
    context_object_name = 'main_map'
