import datetime
import csv
import io
from dateutil import parser
from decimal import Decimal
from itertools import islice

from django.core.cache import cache
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Max, Prefetch
from django.views.generic import View, DetailView, ListView, TemplateView, FormView
from django.urls import reverse

from .models import Station, Datapoint
from .forms import DatapointCsvUploadForm
from .api.views import StationViewSet
from .api.serializers import StationSerializer
from habhub.esp_instrument.models import Deployment
from habhub.ifcb_cruises.models import Cruise


######### AJAX Views to return geoJSON for maps #############
# AJAX views to get GeoJSON responses for all Stations map layer
class StationAjaxGetAllView(View):

    def get(self, request, *args, **kwargs):

        # Get the Station data from the DRF API
        stations_qs = Station.objects.all()
        start_date_obj = None
        end_date_obj = None

        if request.GET:
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            if start_date:
                start_date_obj = datetime.datetime.strptime(start_date, '%m/%d/%Y').date()
            if end_date:
                end_date_obj = datetime.datetime.strptime(end_date, '%m/%d/%Y').date()

        if start_date_obj and end_date_obj:
            stations_qs = stations_qs.prefetch_related(Prefetch(
                'datapoints',
                queryset=Datapoint.objects.filter(measurement_date__range=[start_date_obj, end_date_obj])))

        stations_serializer = StationSerializer(
            stations_qs,
            many=True,
            context={'request': request, 'exclude_dataseries': True}
        )
        stations_list_json = stations_serializer.data

        return JsonResponse(stations_list_json)


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


# Github CSV file importer for Cruises
# If no matching Vessel in RDB based on vessel_name, one will be created
class DatapointCsvUploadView(LoginRequiredMixin, FormView):
    form_class = DatapointCsvUploadForm
    template_name = 'stations/datapoints_upload_form.html'

    def form_valid(self, form):
        csv_file = self.request.FILES['datapoints_csv']
        # Set up the Django file object for CSV DictReader
        csv_file.seek(0)
        reader = csv.DictReader(io.StringIO(csv_file.read().decode('utf-8')))

        errors = list()
        for row in reader:
            # get matching Station object from station_location
            try:
                station = Station.objects.get(station_location=row['station_location'].strip())
            except Station.DoesNotExist:
                error = f"{row['station_location']} - No Matching Station."
                errors.append(error)
                continue

            try:
                measurement_date = parser.parse(row['measurement_date'])
            except Exception as e:
                error = f"{row['station_location']} - {row['measurement_date']} - date error."
                errors.append(error)
                continue

            print(measurement_date)

            try:
                measurement = Decimal(row['measurement'])
            except Exception as e:
                error = f"{row['station_location']} - {row['measurement_date']} - decimal error."
                errors.append(error)
                continue

            if measurement < 0:
                measurement = 40.0

            datapoint = Datapoint.objects.create(
                station=station,
                measurement_date=measurement_date,
                measurement=measurement,
                species_tested=row['species_tested']
            )
        #return reverse('stations:datapoints_import_upload_success', errors)
        return HttpResponse('<h1>Import complete - %s</h1> ' % (errors))
        #return super(DatapointCsvUploadView, self).form_valid(form)

    def get_success_url(self):
        return reverse('stations:datapoints_import_upload_success', )


class DatapointCsvUploadSuccessView(TemplateView):
    template_name = "stations/import_upload_success.html"
