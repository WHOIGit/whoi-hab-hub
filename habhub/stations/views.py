import datetime

from django.core.cache import cache
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg, Max
from django.views.generic import View, DetailView, ListView, TemplateView

from .models import Station, Datapoint
from .api.views import StationViewSet
from .api.serializers import StationSerializer
from habhub.esp_instrument.models import Deployment
from habhub.ifcb_cruises.models import Cruise


########## Functions to use within Station CBVs ###########
"""
Function to build custom JSON objects to return Station objects.
Returns JSON
Args: 'stations_qs' - Django queryset of Station model
"""
def _build_stations_geojson(stations_qs):

    geojson_data = {
        'type': 'FeatureCollection',
        'features': [],
        'crs': {
            'href': 'https://spatialreference.org/ref/epsg/4326/',
            'type': 'proj4'
        }
    }

    for station in stations_qs:
        station_aggs = station.datapoints.aggregate(Avg('measurement'), Max('measurement'))
        station_mean = round(station.station_mean)
        station_max = round(station.station_max)

        station_data = {"type": "Feature",
                        "properties": {
                            "station_name":  station.station_name,
                            "id":  station.id,
                            "state": station.state,
                            "station_location": station.station_location,
                            "datapoint_count": station.datapoints.count(),
                            "station_mean": float(station_mean),
                            "station_max": float(station_max),
                            },
                        "geometry": {
                          "type": station.geom.geom_type,
                          "coordinates": station.geom.coords,
                          }
                        }
        geojson_data['features'].append(station_data)

    return geojson_data

"""
Function to build custom JSON objects to return Station objects filtered by date.
Returns JSON
Args: 'stations_qs' - Django queryset of Station model
      'start_date_obj' - Python date object
      'end_date_obj' - Python date object
"""
def _build_stations_filtered_geojson(stations_qs, start_date_obj, end_date_obj):

    geojson_data = {
        'type': 'FeatureCollection',
        'features': [],
        'crs': {
            'href': 'https://spatialreference.org/ref/epsg/4326/',
            'type': 'proj4'
        }
    }

    for station in stations_qs:
        datapoints_qs = station.datapoints.filter(measurement_date__range=[start_date_obj, end_date_obj])
        station_aggs = datapoints_qs.aggregate(Avg('measurement'), Max('measurement'))
        station_mean = round(station_aggs['measurement__avg'], 1)
        station_max = round(station_aggs['measurement__max'], 1)

        station_data = {"type": "Feature",
                        "properties": {
                            "station_name":  station.station_name,
                            "id":  station.id,
                            "state": station.state,
                            "station_location": station.station_location,
                            "datapoint_count": station.datapoints.count(),
                            "station_mean": float(station_mean),
                            "station_max": float(station_max),
                            },
                        "geometry": {
                          "type": station.geom.geom_type,
                          "coordinates": station.geom.coords,
                          }
                        }
        geojson_data['features'].append(station_data)

    return geojson_data


######### AJAX Views to return geoJSON for maps #############

# Function to load data for each Station dynamically on marker click
def load_station_data(request):
    station_id = request.GET.get('station_id')

    if station_id:
        station = Station.objects.get(id=station_id)
    else:
        station = None
    return render(request, 'stations/station_popup.html', {'station': station})


######### AJAX Views to return geoJSON for maps #############
# AJAX views to get GeoJSON responses for all Stations map layer
class StationAjaxGetAllView(View):

    def get(self, request, *args, **kwargs):

        stations_list_json = cache.get('stations_list_json')
        if not stations_list_json:
            # Get the Station data from the DRF API
            stations_qs = Station.objects.all()
            stations_serializer = StationSerializer(
                stations_qs,
                many=True,
                context={'request': request, 'exclude_dataseries': True}
            )
            stations_list_json = stations_serializer.data
            #stations_list_json = StationViewSet.as_view({'get': 'list', 'exclude_dataseries':'true'})(request).data
            cache.set('stations_list_json', stations_list_json, 60)

        return JsonResponse(stations_list_json)


# AJAX views to get GeoJSON responses for Stations map layer filtered by date
class StationAjaxGetFilteredView(View):

    def get(self, request, *args, **kwargs):
        stations_qs = Station.objects.all()
        # Check if there are search query parameters in the AJAX request, assign variables
        if request.GET:
            start_date = request.GET.get('start-date')
            end_date = request.GET.get('end-date')
            start_date_obj = None
            end_date_obj = None

            if start_date:
                start_date_obj = datetime.datetime.strptime(start_date, '%m/%d/%Y').date()
            if end_date:
                end_date_obj = datetime.datetime.strptime(end_date, '%m/%d/%Y').date()

            # Chain extra filter queries if used.
            if start_date_obj and end_date_obj:
                stations_qs = stations_qs.filter(datapoints__measurement_date__range=[start_date_obj, end_date_obj])

        geojson_data = _build_stations_filtered_geojson(stations_qs, start_date_obj, end_date_obj)
        return JsonResponse(geojson_data)


# AJAX views to get GeoJSON responses for all Stations map layer
class StationAjaxGetChartView(View):

    def get(self, request, *args, **kwargs):
        station_id = self.kwargs['station_id']

        try:
            station_obj = Station.objects.get(id=station_id)
        except:
            station_obj = None

        print(station_obj)
        if station_obj:
            datapoints_qs = station_obj.datapoints.all()
            datapoint_series_data = list()

            for datapoint in datapoints_qs:
                date_str = datapoint.measurement_date.strftime('%Y-%m-%d')
                datapoint_series_data.append([date_str, float(datapoint.measurement)])

            x_axis = {
                'type': 'datetime',
            }

            y_axis = {
                'title': 'Shellfish meat toxicity',
                'min': 0,
                'softMax': 150,
                'plotLines': [{
                    'value': 80,
                    'color': 'red',
                    'dashStyle': 'shortdash',
                    'width': 2,
                    'label': {
                        'text': 'Closure threshold'
                    }
                }]
            }

            plot_options = {'series': {'threshold': 100}}

            datapoint_series = {
                'name': 'Shellfish meat toxicity',
                'data': datapoint_series_data,
            }

            chart = {
                'chart': {'type': 'spline'},
                'title': {'text': station_obj.station_location},
                'yAxis': y_axis,
                'xAxis': x_axis,
                'plotOptions': plot_options,
                #'plotOptions': plot_options,
                'series': [datapoint_series],
            }

        return JsonResponse(chart)


######### CBV Views for basic templates #############
class StationMapMainView(TemplateView):
    template_name = 'stations/stations_map_main.html'

    def get_context_data(self, **kwargs):
        context = super(StationMapMainView, self).get_context_data(**kwargs)
        # Get the earliest available notice date for the filter form
        datapoint_obj = Datapoint.objects.earliest()
        earliest_date = datapoint_obj.measurement_date.strftime("%m/%d/%Y")

        context.update({
            'earliest_date': earliest_date,
        })
        return context


class StationListView(ListView):
    model = Station
    template_name = 'stations/station_list.html'
    context_object_name = 'stations'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the ESP Deployments
        context['esp_deployments'] = Deployment.objects.all()
        # Add in a QuerySet of all the IFCB Cruises
        context['ifcb_cruises'] = Cruise.objects.all()
        return context
