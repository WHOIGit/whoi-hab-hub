import datetime

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.generic import View, DetailView, TemplateView

from .models import *
from .api.serializers import DatasetSerializer

######### AJAX Views to return geoJSON for maps #############
# AJAX views to get GeoJSON responses for all IFCB Dataset map layer
class DatasetAjaxGetAllView(View):

    def get(self, request, *args, **kwargs):

        # Get the Station data from the DRF API
        dataset_qs = Dataset.objects.all()
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
            dataset_qs = dataset_qs.prefetch_related(Prefetch(
                'bins',
                queryset=Bin.objects.filter(sample_time__range=[start_date_obj, end_date_obj])))

        dataset_serializer = DatasetSerializer(
            dataset_qs,
            many=True,
            context={'request': request, 'exclude_dataseries': True}
        )
        dataset_list_json = dataset_serializer.data

        return JsonResponse(dataset_list_json)


######### CBV Views for basic templates #############
class IFCBMapMainView(TemplateView):
    template_name = 'ifcb_datasets/ifcb_map_main.html'

    def get_context_data(self, **kwargs):
        context = super(IFCBMapMainView, self).get_context_data(**kwargs)
        # Get the earliest available notice date for the filter form
        bin_obj = Bin.objects.earliest()
        earliest_date = bin_obj.sample_time.strftime("%m/%d/%Y")

        context.update({
            'earliest_date': earliest_date,
        })
        return context
