from celery import shared_task

from .requests import run_species_classifed_import
from .models import Dataset


@shared_task
def hello():
    print('Howdy')


@shared_task(time_limit=300, soft_time_limit=300)
def get_ifcb_dashboard_data():
    sets = Dataset.objects.all()
    print(sets)
    for set in sets:
        print(set)
        run_species_classifed_import(set)
        print("set complete")
