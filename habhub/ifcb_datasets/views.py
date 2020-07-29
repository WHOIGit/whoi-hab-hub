import datetime
from statistics import mean

from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.generic import View, DetailView, TemplateView
from django.db.models import Avg, Max, Prefetch
from django.contrib.postgres.fields.jsonb import KeyTransform, KeyTextTransform

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
        # Get past week concentration data across Datasets
        concentrations_pastweek = []
        daylastweek = timezone.now().date() - datetime.timedelta(days=7)
        dataset_qs = Dataset.objects.order_by('id').prefetch_related(Prefetch(
            'bins',
            queryset=Bin.objects.filter(sample_time__gte=daylastweek)))

        for dataset in dataset_qs:
            data = {'dataset': dataset.__str__(), 'values': [], }
            for species in Bin.TARGET_SPECIES:
                concentration_vals = []
                if dataset.bins.exists():
                    for bin in dataset.bins.all():
                        item = bin.get_concentration_data_by_species(species[0])
                        if item:
                            concentration_vals.append(item['cell_concentration'])
                    max_val = max(concentration_vals)
                    mean_val = int(mean(concentration_vals))
                    data['values'].append({'species' : species[1], 'max' : max_val, 'mean' : mean_val, })
            concentrations_pastweek.append(data)

        context.update({
            'earliest_date': earliest_date,
            'concentrations_pastweek': concentrations_pastweek,
        })
        return context


######### AJAX Views for partial templates #############
# Function to load Parts based on Part Number Search
class DatasetAjaxGetMapSidebar(View):

    def get(self, request, *args, **kwargs):
        dataset_obj = None
        # check if there's a PK kwarg, if so return Detail template
        pk = self.kwargs.get('pk', None)
        if pk:
            dataset_obj = get_object_or_404(Dataset, pk=pk)
            # Assemble some meta data and image data
            # Get the earliest available notice date for the filter form
            first_bin = dataset_obj.bins.earliest()
            last_bin = dataset_obj.bins.latest()
            # Get species data
            images = []
            concentrations_pastweek = []
            TARGET_SPECIES = Bin.TARGET_SPECIES

            for species in TARGET_SPECIES:
                # Get images
                latest_image_bin = dataset_obj.bins.filter(species_found__contains=[species[0]]).latest()
                print(latest_image_bin, latest_image_bin.id)
                data = latest_image_bin.get_concentration_data_by_species(species[0])
                img_name = F"ifcb/images/{data['image_numbers'][0]}.png"
                images.append((species[1], img_name))
                print(img_name)

            dashboard_data = {
                'earliest_date': first_bin.sample_time,
                'latest_date': last_bin.sample_time,
                'depth': last_bin.depth,
                'total_bins': dataset_obj.bins.count(),
                'images': images,
                #'concentrations_pastweek': concentrations_pastweek,
            }
            return render(request, 'ifcb_datasets/_dashboard_sidebar_detail.html', {'dataset_obj': dataset_obj, 'dashboard_data': dashboard_data,})
        # If no pk, return the main "home" sidebar template
        # Get past week concentration data across Datasets
        concentrations_pastweek = []
        daylastweek = timezone.now().date() - datetime.timedelta(days=7)
        dataset_qs = Dataset.objects.order_by('id').prefetch_related(Prefetch(
            'bins',
            queryset=Bin.objects.filter(sample_time__gte=daylastweek)))

        for dataset in dataset_qs:
            data = {'dataset': dataset.__str__(), 'values': [], }
            for species in Bin.TARGET_SPECIES:
                concentration_vals = []
                if dataset.bins.exists():
                    for bin in dataset.bins.all():
                        item = bin.get_concentration_data_by_species(species[0])
                        if item:
                            concentration_vals.append(item['cell_concentration'])
                    max_val = max(concentration_vals)
                    mean_val = int(mean(concentration_vals))
                    data['values'].append({'species' : species[1], 'max' : max_val, 'mean' : mean_val, })
            concentrations_pastweek.append(data)
        return render(request, 'ifcb_datasets/_dashboard_sidebar_home.html', {'concentrations_pastweek': concentrations_pastweek,})
