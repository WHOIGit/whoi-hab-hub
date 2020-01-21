from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core.serializers import serialize
from django.views.generic import View, DetailView, ListView, TemplateView
from djgeojson.views import GeoJSONResponseMixin

from .models import *
# Create your views here.

class ClosureMapView(TemplateView):
    template_name = 'closures/closures_map.html'
    context_object_name = 'closures'


# AJAX views to get GeoJSON responses for maps
class ClosureAjaxGetAllView(View):

    def get(self, request, *args, **kwargs):
        # Get Closure notice data, format for GeoJson response
        #closures_qs = ClosureNotice.objects.filter(shellfish_areas__isnull=False).prefetch_related('shellfish_areas')
        closures_qs = ClosureNotice.objects.all().prefetch_related('shellfish_areas')
        #closures_qs = ClosureNotice.objects.filter(id=6)
        print(closures_qs.count())
        geojson_data = {
            'type': 'FeatureCollection',
            'features': []
        }

        for closure in closures_qs:
            for shellfish_area in closure.shellfish_areas.all():
                if shellfish_area.state == 'MA':
                    if closure.custom_geom:
                        geom = closure.custom_geom.simplify(0.001).coords
                    elif not shellfish_area.geom.empty:
                        geom = shellfish_area.geom.simplify(0.001).coords
                    else:
                        geom = None

                    print(geom, shellfish_area.id)
                    closure_data = {"type": "Feature",
                                    "properties": {
                                        "title":  closure.title,
                                        "id":  closure.id },
                                    "geometry": {
                                      "type": shellfish_area.geom.geom_type,
                                      "coordinates": geom }
                                    }
                    if geom:
                        geojson_data['features'].append(closure_data)
        return JsonResponse(geojson_data)


class ClosureHomeView(TemplateView):
    template_name = 'closures/closures_home.html'
    context_object_name = 'closures'


class ClosureHomeView2(TemplateView):
    template_name = 'closures/closures_home2.html'
    context_object_name = 'closures'


class ClosureHomeView3(TemplateView):
    template_name = 'closures/closures_home3.html'
    context_object_name = 'closures'

    def get_context_data(self, **kwargs):
        context = super(ClosureHomeView3, self).get_context_data(**kwargs)
        queryset = ShellfishArea.objects.filter(current_status='Closed').values('id', 'name')
        closures_list = list(queryset)  # important: convert the QuerySet to a list object)

        context.update({
            'closures_list': JsonResponse(closures_list, safe=False),
        })
        return context


class ClosureAreaAjaxView(View):

    def get(self, request, *args, **kwargs):
        queryset = ShellfishArea.objects.filter(current_status='Closed').order_by('-acres').values('id', 'name')
        closures_list = list(queryset)  # convert the QuerySet to a list object)
        return JsonResponse(closures_list, safe=False)


class ClosureAreaAjaxGeoLayerByStateView(GeoJSONResponseMixin, ListView):
    model = ShellfishArea
    properties = ['name']

    def get_queryset(self):
        state_code = self.kwargs['state_code']
        queryset = ShellfishArea.objects.filter(state=state_code)
        return queryset


class ClosureAreaAjaxGeoLayerSingleView(GeoJSONResponseMixin, ListView):
    model = ShellfishArea
    properties = ['name']

    def get_queryset(self):
        feature_id = self.kwargs['pk']
        queryset = ShellfishArea.objects.filter(id=feature_id)
        return queryset


class ClosureAreaAjaxGeoLayerByStatusView(GeoJSONResponseMixin, ListView):
    model = ShellfishArea
    properties = ['name']
    simplify = 0.5

    def get_queryset(self):
        current_status = self.kwargs['current_status']
        queryset = ShellfishArea.objects.filter(current_status=current_status)
        return queryset
