from celery import shared_task
from django.core.cache import cache

from .api_requests import (
    run_species_classifed_import,
    reset_ifcb_data,
    _calculate_metrics,
)


@shared_task(time_limit=84600, soft_time_limit=84600)
def get_ifcb_dashboard_data():
    from .models import Dataset

    sets = Dataset.objects.all()
    for set in sets:
        print(set)
        run_species_classifed_import(set)
        print("set complete")
    # clear the cache of stale results
    cache.clear()


@shared_task(time_limit=345600, soft_time_limit=345600, bind=True)
def reset_ifcb_dataset_data(self, dataset_id=None):
    print("DATASET ID ", dataset_id)
    reset_ifcb_data(dataset_id)
    # clear the cache of stale results
    cache.clear()


@shared_task(time_limit=84600, soft_time_limit=84600, bind=True)
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
    # clear the cache of stale results
    cache.clear()
