from celery import shared_task
from django.core.cache import cache

from .api_requests import (
    run_species_classifed_import,
    reset_ifcb_data,
    _calculate_metrics,
)


@shared_task(time_limit=3000, soft_time_limit=3000)
def get_ifcb_dashboard_data():
    from .models import Dataset

    sets = Dataset.objects.all()
    for set in sets:
        print(set)
        run_species_classifed_import(set)
        print("set complete")


@shared_task(time_limit=20000, soft_time_limit=20000)
def reset_ifcb_dataset_data():
    reset_ifcb_data()


@shared_task(time_limit=20000, soft_time_limit=20000, bind=True)
def recalculate_metrics(self, species_id=None):
    from .models import Bin

    print(self.request.id, self.request)
    cache_key = f"{self.request.task}-{species_id}"
    cache.set(cache_key, self.request.id)

    if species_id:
        bins = Bin.objects.filter(species_found__contains=[species_id])
    else:
        bins = Bin.objects.all()

    for bin in bins:
        _calculate_metrics(bin)
