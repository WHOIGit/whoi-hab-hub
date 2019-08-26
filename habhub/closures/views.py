from django.shortcuts import render
from django.views.generic import View, DetailView, ListView, TemplateView
from djgeojson.views import GeoJSONResponseMixin

from .models import ClosureArea
# Create your views here.


class ClosureHomeView(TemplateView):
    template_name = 'closures/closures_home.html'
    context_object_name = 'closures'


class ClosureHomeView2(TemplateView):
    template_name = 'closures/closures_home2.html'
    context_object_name = 'closures'


class ClosureHomeView3(TemplateView):
    template_name = 'closures/closures_home3.html'
    context_object_name = 'closures'


class ClosureAreaAjaxGeoLayerByStateView(GeoJSONResponseMixin, ListView):
    model = ClosureArea
    properties = ['name']

    def get_queryset(self):
        state_code = self.kwargs['state_code']
        queryset = ClosureArea.objects.filter(state=state_code)
        return queryset


class ClosureAreaAjaxGeoLayerSingleView(GeoJSONResponseMixin, ListView):
    model = ClosureArea
    properties = ['name']

    def get_queryset(self):
        feature_id = self.kwargs['pk']
        queryset = ClosureArea.objects.filter(id=feature_id)
        return queryset


class ClosureAreaAjaxGeoLayerByStatusView(GeoJSONResponseMixin, ListView):
    model = ClosureArea
    properties = ['name']

    def get_queryset(self):
        current_status = self.kwargs['current_status']
        queryset = ClosureArea.objects.filter(current_status=current_status)
        return queryset
