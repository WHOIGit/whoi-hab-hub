import datetime
from statistics import mean
import environ

from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.generic import View, DetailView, TemplateView
from django.db.models import Avg, Max, Prefetch

from habhub.core.models import TargetSpecies
from .models import *
from .utils import _get_image_ifcb_dashboard
from .api.serializers import DatasetListSerializer

env = environ.Env()


# Function to load IFBC map sidebar
class BinAjaxGetImagesBySpecies(View):
    def get(self, request, *args, **kwargs):
        species = request.GET.get("species")
        bin_pid = request.GET.get("bin_pid")
        format = request.GET.get("format")

        images = []
        # AJAX is sending display name
        target_list = TargetSpecies.objects.all()
        species = next(
            (item for item in target_list if item.display_name == species), False
        )
        print(species)
        try:
            bin_obj = Bin.objects.get(pid=bin_pid)
        except Bin.DoesNotExist as e:
            print(e)
            bin_obj = None

        if bin_obj and species:
            data = bin_obj.get_concentration_data_by_species(species.species_id)
            image_numbers = data["image_numbers"][:30]
            public_url = bin_obj.dataset.dashboard_public_url
            if not public_url:
                public_url = bin_obj.dataset.dashboard_base_url

            for img_name in image_numbers:
                img_path = (
                    f"{public_url}/{bin_obj.dataset.dashboard_id_name}/{img_name}.png"
                )
                # need to check is this image exists locally. If not, go get it and cache locally
                # _get_image_ifcb_dashboard(bin_obj.dataset, img_name)
                # img_path = F"media/ifcb/images/{img_name}.png"
                images.append(img_path)

        if format == "json":
            bin_images_json = {
                "bin": {
                    "pid": bin_obj.pid,
                    "dataset_id": bin_obj.dataset.dashboard_id_name,
                },
                "species": species.display_name,
                "images": images,
            }
            return JsonResponse(bin_images_json)
        return render(
            request,
            "ifcb_datasets/_dashboard_sidebar_images_pane.html",
            {"bin_obj": bin_obj, "images": images, "species": species.display_name},
        )
