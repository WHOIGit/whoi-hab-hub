from celery import shared_task
from django.core.cache import cache

from .api_requests import (
    run_species_classifed_import,
    reset_ifcb_data,
    _calculate_metrics,
)
from .api.cache_utils import clear_dataset_summary_cache, clear_spatial_grid_cache
from .locks import ingestion_lock


@shared_task(time_limit=84600, soft_time_limit=84600)
def get_ifcb_dashboard_data():
    from .models import Dataset

    with ingestion_lock(timeout=3600) as acquired:
        if not acquired:
            print("IFCB ingestion already in progress, skipping this run.")
            return

        sets = Dataset.objects.all()
        for set in sets:
            print(set)
            run_species_classifed_import(set, 100)
            print("set complete")
            # clear only this dataset's stale cached results
            clear_dataset_summary_cache(set.id)
        clear_spatial_grid_cache()

@shared_task(time_limit=84600, soft_time_limit=84600)
def get_ifcb_dashboard_data_high_priority():
    from .models import Dataset

    with ingestion_lock(timeout=3600) as acquired:
        if not acquired:
            print("IFCB ingestion already in progress, skipping this run.")
            return

        print("run high priority data ingestion")
        sets = Dataset.objects.filter(high_priority_updates=True)
        for set in sets:
            print(set)
            run_species_classifed_import(set, None)
            print("set complete")
            # clear only this dataset's stale cached results
            clear_dataset_summary_cache(set.id)
        clear_spatial_grid_cache()

@shared_task(time_limit=345600, soft_time_limit=345600, bind=True)
def reset_ifcb_dataset_data(self, dataset_id=None, start_date=None, end_date=None):
    from .models import Dataset

    with ingestion_lock(timeout=21600) as acquired:
        if not acquired:
            print("IFCB ingestion already in progress, skipping this reset.")
            return

        print("DATASET ID ", dataset_id)
        print("Task Dates: ", start_date, end_date)
        reset_ifcb_data(dataset_id, start_date, end_date)
        # clear stale cached results for the affected dataset(s)
        if dataset_id:
            clear_dataset_summary_cache(dataset_id)
        else:
            for id in Dataset.objects.values_list("id", flat=True):
                clear_dataset_summary_cache(id)
        clear_spatial_grid_cache()


@shared_task(time_limit=84600, soft_time_limit=84600, bind=True)
def recalculate_metrics(self, species_id=None):
    from .models import Bin

    print(self.request.id, self.request)
    cache_key = f"{self.request.task}-{species_id}"
    cache.set(cache_key, self.request.id)

    with ingestion_lock(timeout=21600) as acquired:
        if not acquired:
            print("IFCB ingestion already in progress, skipping this recalculation.")
            return

        if species_id:
            bins = Bin.objects.filter(species_found__contains=[species_id])
        else:
            bins = Bin.objects.all()

        for bin in bins:
            _calculate_metrics(bin)

        # clear stale cached results for every dataset touched by these bins
        for id in bins.values_list("dataset_id", flat=True).distinct():
            clear_dataset_summary_cache(id)
        clear_spatial_grid_cache()
