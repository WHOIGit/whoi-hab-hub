import random

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core.serializers import serialize
from django.views.generic import View, DetailView, ListView, TemplateView
from djgeojson.views import GeoJSONResponseMixin

from .models import *

from django.contrib.gis.db.models.functions import GeoFunc
from django.db.models import Value

class GeneratePoints(GeoFunc):
    function='ST_GeneratePoints'

########## Functions to use within Closure CBVs ###########


"""
Function to build custom JSON objects to return ClosureDataEvent objects.
Returns JSON
Args: 'events_qs' - Django queryset of ClosureDataEvent model, 'notice_obj' object
"""
def _build_closure_data_event_by_notice_geojson(events_qs, notice_obj):
    geojson_data = {
            'closure_notice': notice_obj.title,
            'closure_id': notice_obj.id,
            'shellfish_area': events_qs.first().shellfish_area.name,
            'shellfish_area_description': events_qs.first().shellfish_area.area_description,
            'effective_date': notice_obj.effective_date,
            'total_duration': notice_obj.get_total_closure_duration(),
            'features': [],
    }

    for event in events_qs:
        if event.get_closure_duration():
            duration = '%s days' % (event.get_closure_duration().days)
        else:
            duration = 'Ongoing'

        event_data = {'event': {
                            'title':  event.__str__(),
                            'id':  event.id,
                            'shellfish_area': event.shellfish_area.name,
                            'year': event.effective_date.year,
                            'month': event.effective_date.month,
                            'species': event.species.name,
                            'duration': duration,
                            },
                        }

        geojson_data['features'].append(event_data)

    return geojson_data

"""
Function to build custom JSON objects to return ClosureDataEvent objects.
Returns JSON
Args: 'events_qs' - Django queryset of ClosureDataEvent model
"""
def _build_closure_data_event_geojson(events_qs):
    geojson_data = {
            'features': [],
    }

    for event in events_qs:
        event_data = {"event": {
                            "title":  event.__str__(),
                            "id":  event.id,
                            "shellfish_area": event.shellfish_area.name,
                            "year": event.effective_date.year,
                            "month": event.effective_date.month,
                            "species": event.species.name,
                            },
                        }

        geojson_data['features'].append(event_data)

    return geojson_data


"""
Function to build cusom geojson objects to populate the dynamic maps
Args: 'closures_qs' - Django queryset of ClosureNotice model
"""

def _build_closure_notice_geojson(closures_qs):
    geojson_data = {
        'type': 'FeatureCollection',
        'features': [],
        'crs': {
            'href': 'https://spatialreference.org/ref/epsg/4326/',
            'type': 'proj4'
        }
    }

    for closure in closures_qs:
        for shellfish_area in closure.shellfish_areas.all():

            if closure.custom_geom:
                geom = closure.custom_geom.simplify(0.0001)
                # Need to check if the simplify method went too far and made the geom empty
                if shellfish_area.geom.simplify(0.0001).empty:
                    geom = shellfish_area.geom
            elif not shellfish_area.geom.empty:
                geom = shellfish_area.geom.simplify(0.0001)
                #geom = shellfish_area.geom
                # Need to check if the simplify method went too far and made the geom empty
                if not geom.geom_type == "MultiPolygon":
                    geom = shellfish_area.geom
            else:
                geom = None

            closure_data = {"type": "Feature",
                            "properties": {
                                "title":  closure.title,
                                "id":  closure.id,
                                "state": shellfish_area.state,
                                "year": closure.effective_date.year,
                                "month": closure.effective_date.month,
                                "species": [species.name for species in closure.species.all()],
                                },
                            "geometry": {
                              "type": shellfish_area.geom.geom_type,
                              "coordinates": geom.coords,
                              }
                            }
            if geom:
                geojson_data['features'].append(closure_data)

    return geojson_data


"""
Function to build custom geojson objects to populate the dynamic maps.
Returns the center Point of polygonal shellfish areas instead of shape.
Args: 'closures_qs' - Django queryset of ClosureNotice model
"""
def _build_closure_notice_points_geojson(closures_qs):
    geojson_data = {
        'type': 'FeatureCollection',
        'features': [],
        'crs': {
            'href': 'https://spatialreference.org/ref/epsg/4326/',
            'type': 'proj4'
        }
    }

    for closure in closures_qs:
        for shellfish_area in closure.shellfish_areas.all():

            if closure.custom_geom:
                geom = closure.custom_geom.simplify(0.001)
                # Need to check if the simplify method went too far and made the geom empty
                if shellfish_area.geom.simplify(0.001).empty:
                    geom = shellfish_area.geom
            elif not shellfish_area.geom.empty:
                geom = shellfish_area.geom.simplify(0.001)
                #geom = shellfish_area.geom
                # Need to check if the simplify method went too far and made the geom empty
                if not geom.geom_type == "MultiPolygon":
                    geom = shellfish_area.geom
            else:
                geom = None

            if geom:
                geom = geom.centroid

            if closure.causative_organism:
                causative_organism = closure.causative_organism.name
            else:
                causative_organism = 'Unknown'

            closure_data = {"type": "Feature",
                            "properties": {
                                "title":  closure.title,
                                "id":  closure.id,
                                "shellfish_area_id": shellfish_area.id,
                                "shellfish_area_name": shellfish_area.name,
                                "shellfish_area_description": shellfish_area.area_description,
                                "state": shellfish_area.state,
                                "year": closure.effective_date.year,
                                "month": closure.effective_date.month,
                                "species": [species.name for species in closure.species.all()],
                                "causative_organism": causative_organism,
                                "effective_date" : closure.effective_date,
                                },
                            "geometry": {
                              "type": geom.geom_type,
                              "coordinates": geom.coords,
                              }
                            }
            if geom:
                geojson_data['features'].append(closure_data)

    return geojson_data


"""
Function to build custom geojson objects to populate the dynamic maps.
Returns the Point on circle around the centroid of polygonal shellfish areas instead of shape.
Args: 'closures_qs' - Django queryset of ClosureNotice model
"""
def _build_closure_notice_circle_points_geojson(closures_qs):
    geojson_data = {
        'type': 'FeatureCollection',
        'features': [],
        'crs': {
            'href': 'https://spatialreference.org/ref/epsg/4326/',
            'type': 'proj4'
        }
    }

    for closure in closures_qs:
        for shellfish_area in closure.shellfish_areas.all().annotate(rand_point=GeneratePoints(
                                                                'geom',
                                                                Value(1) # to get only one point
                                                            )):

            if closure.custom_geom:
                geom = closure.annotate(rand_point=GeneratePoints(
                            'custom_geom',
                            Value(1) # to get only one point
                        ))

            elif not shellfish_area.geom.empty:
                geom = shellfish_area.rand_point
            else:
                geom = None

            print(geom.coords)

            closure_data = {"type": "Feature",
                            "properties": {
                                "title":  closure.title,
                                "id":  closure.id,
                                "state": shellfish_area.state,
                                "year": closure.effective_date.year,
                                "month": closure.effective_date.month,
                                "species": [species.name for species in closure.species.all()],
                                },
                            "geometry": {
                              "type": 'Point',
                              "coordinates": geom.coords[0],
                              }
                            }
            if geom:
                geojson_data['features'].append(closure_data)

    return geojson_data

######### AJAX Views to return geoJSON for maps #############
# AJAX views to get GeoJSON responses for map layers by State code
class ClosureDataEventAjaxGetByAreaView(View):

    def get(self, request, *args, **kwargs):
        # Get Closure notice data, format for GeoJson response
        shellfish_area_id = self.kwargs['shellfish_area_id']
        events_qs = ClosureDataEvent.objects.filter(shellfish_area__id=shellfish_area_id) \
                                        .filter(notice_action='Closed') \
                                        .order_by('effective_date')
        print(events_qs.count())
        geojson_data = _build_closure_data_event_geojson(events_qs)
        return JsonResponse(geojson_data)


# AJAX views to get GeoJSON responses for map layers by State code
class ClosureDataEventAjaxGetByNoticeView(View):

    def get(self, request, *args, **kwargs):
        # Get Closure notice data, format for GeoJson response
        notice_id = self.kwargs['notice_id']
        shellfish_area_id = self.kwargs['shellfish_area_id']

        try:
            notice_obj = ClosureNotice.objects.get(id=notice_id)
        except ClosureNotice.DoesNotExist:
            notice_obj = None

        events_qs = ClosureDataEvent.objects.filter(closure_notice__id=notice_id) \
                                        .filter(shellfish_area__id=shellfish_area_id) \
                                        .filter(notice_action='Closed') \
                                        .order_by('effective_date')
        print(events_qs.count())
        geojson_data = _build_closure_data_event_by_notice_geojson(events_qs, notice_obj)
        return JsonResponse(geojson_data)


# AJAX views to get all ClosureNotice objects for maps
class ClosureNoticeAjaxGetAllView(View):

    def get(self, request, *args, **kwargs):
        # Get Closure notice data, format for GeoJson response
        closures_qs = ClosureNotice.objects.filter(notice_action='Closed') \
                                           .exclude(shellfish_areas__state='ME') \
                                           .distinct() \
                                           .prefetch_related('shellfish_areas')
        print(closures_qs.count())
        # Create custom geojson response object with custom function
        geojson_data = _build_closure_notice_geojson(closures_qs)
        return JsonResponse(geojson_data)


# AJAX views to get GeoJSON responses for map layers by State code
class ClosureNoticeAjaxGetLayerByStateView(View):

    def get(self, request, *args, **kwargs):
        # Get Closure notice data, format for GeoJson response
        state_code = self.kwargs['state_code']
        closures_qs = ClosureNotice.objects.filter(notice_action='Closed').filter(shellfish_areas__state=state_code).distinct().prefetch_related('shellfish_areas')
        print(closures_qs.count())
        geojson_data = _build_closure_notice_geojson(closures_qs)
        return JsonResponse(geojson_data)


# AJAX views to get all ClosureNotice objects for maps
class ClosureNoticeAjaxGetAllPointsView(View):

    def get(self, request, *args, **kwargs):
        # Get Closure notice data, format for GeoJson response
        closures_qs = ClosureNotice.objects.filter(notice_action='Closed') \
                                           .exclude(shellfish_areas__state='ME') \
                                           .distinct() \
                                           .prefetch_related('shellfish_areas')
        print(closures_qs.count())
        # Create custom geojson response object with custom function
        geojson_data = _build_closure_notice_points_geojson(closures_qs)
        return JsonResponse(geojson_data)


# AJAX views to get GeoJSON responses for map layers by State code
class ClosureNoticeAjaxGetLayerByStatePointsView(View):

    def get(self, request, *args, **kwargs):
        # Get Closure notice data, format for GeoJson response
        state_code = self.kwargs['state_code']
        closures_qs = ClosureNotice.objects.filter(notice_action='Closed') \
                                        .filter(shellfish_areas__state=state_code) \
                                        .distinct().prefetch_related('shellfish_areas') \
                                        .order_by('effective_date')
        geojson_data = _build_closure_notice_points_geojson(closures_qs)
        return JsonResponse(geojson_data)


# AJAX views to get GeoJSON responses for map layers by State code
class ClosureNoticeAjaxGetLayerByStatePointsCircleView(View):

    def get(self, request, *args, **kwargs):
        # Get Closure notice data, format for GeoJson response
        state_code = self.kwargs['state_code']
        closures_qs = ClosureNotice.objects.filter(notice_action='Closed').filter(shellfish_areas__state=state_code).distinct().prefetch_related('shellfish_areas')
        print(closures_qs.count())
        geojson_data = _build_closure_notice_circle_points_geojson(closures_qs)
        return JsonResponse(geojson_data)


######### CBV Views for basic templates #############
class ClosureMapShapeView(TemplateView):
    template_name = 'closures/closures_map_shapes.html'
    context_object_name = 'closures'


class ClosureMapClusterView(TemplateView):
    template_name = 'closures/closures_map_cluster.html'
    context_object_name = 'closures'


class ClosureMapClusterView2(TemplateView):
    template_name = 'closures/closures_map_cluster2.html'
    context_object_name = 'closures'


class ClosureMapClusterNoSpiderView(TemplateView):
    template_name = 'closures/closures_map_cluster_nospider.html'
    context_object_name = 'closures'


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
    #simplify = 0.0001

    def get_queryset(self):
        feature_id = self.kwargs['pk']
        queryset = ShellfishArea.objects.filter(id=feature_id)
        return queryset


class ClosureAreaAjaxGeoLayerByStatusView(GeoJSONResponseMixin, ListView):
    model = ShellfishArea
    properties = ['name']
    simplify = 0.0001

    def get_queryset(self):
        current_status = self.kwargs['current_status']
        queryset = ShellfishArea.objects.filter(current_status=current_status)
        return queryset
