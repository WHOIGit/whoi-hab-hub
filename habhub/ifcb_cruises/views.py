from django.shortcuts import render
from django.views.generic import View, DetailView, ListView

from .models import Cruise, IFCBDatapoint

# AJAX Views

# Function to load data for each IFCB datapoint dynamically on marker click
def load_ifcb_cruise_data(request):
    ifcb_datapoint_id = request.GET.get('stationifcb_datapoint_id_id')

    if ifcb_datapoint_id:
        datapoint = IFCBDatapoint.objects.get(id=ifcb_datapoint_id)
    else:
        datapoint = None
    return render(request, 'ifcb_cruises/datapoint_popup.html', {'datapoint': datapoint})
