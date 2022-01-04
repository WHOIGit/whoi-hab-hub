from celery import shared_task

from .api_requests import run_species_classifed_import, reset_ifcb_data


@shared_task(time_limit=3000, soft_time_limit=3000)
def get_ifcb_dashboard_data():
    from .models import Dataset

    sets = Dataset.objects.all()
    for set in sets:
        print(set)
        run_species_classifed_import(set)
        print("set complete")


@shared_task(time_limit=20000, soft_time_limit=20000)
def reset_ifcb_dashboard_data():
    reset_ifcb_data()
