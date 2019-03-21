from django.shortcuts import render
from django.views.generic import View, DetailView, ListView

from .models import Station, Datapoint
from habhub.esp_instrument.models import Deployment
from habhub.ifcb_cruises.models import Cruise

# AJAX Views

# Function to load data for each Station dynamically on marker click
def load_station_data(request):
    station_id = request.GET.get('station_id')

    if station_id:
        station = Station.objects.get(id=station_id)
    else:
        station = None
    return render(request, 'stations/station_popup.html', {'station': station})

# CBV Views to generate site pages

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
