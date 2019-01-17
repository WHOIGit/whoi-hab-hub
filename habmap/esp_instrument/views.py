from django.shortcuts import render
from django.views.generic import View, DetailView, ListView

from .models import EspInstrument, Deployment

# AJAX Views

# Function to load data for each ESP Deployment dynamically on marker click
def load_esp_deployment_data(request):
    esp_deployment_id = request.GET.get('esp_deployment_id')

    if esp_deployment_id:
        esp_deployment = Deployment.objects.get(id=esp_deployment_id)
    else:
        esp_deployment = None
    return render(request, 'esp_instrument/esp_deployment_popup.html', {'esp_deployment': esp_deployment})
