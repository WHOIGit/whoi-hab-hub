from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.generic import View, DetailView, ListView, TemplateView

from .models import Station, Datapoint
from habhub.esp_instrument.models import Deployment
from habhub.ifcb_cruises.models import Cruise


########## Functions to use within Closure CBVs ###########
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
        station_data = {"type": "Feature",
                        "properties": {
                            "station_name":  station.station_name,
                            "id":  station.id,
                            "state": station.state,
                            "station_location": station.station_location,
                            "datapoint_count": station.datapoints.count(),
                            },
                        "geometry": {
                          "type": station.geom.geom_type,
                          "coordinates": station.geom.coords,
                          }
                        }
        geojson_data['features'].append(station_data)

    return geojson_data


# AJAX Views

# Function to load data for each Station dynamically on marker click
def load_station_data(request):
    station_id = request.GET.get('station_id')

    if station_id:
        station = Station.objects.get(id=station_id)
    else:
        station = None
    return render(request, 'stations/station_popup.html', {'station': station})


######### AJAX Views to return geoJSON for maps #############
# AJAX views to get GeoJSON responses for map layers by State code
class StationAjaxGetAllView(View):

    def get(self, request, *args, **kwargs):
        stations_qs = Station.objects.all()
        geojson_data = _build_stations_geojson(stations_qs)
        return JsonResponse(geojson_data)


######### CBV Views for basic templates #############
class StationMapMainView(TemplateView):
    template_name = 'stations/stations_map_main.html'


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
