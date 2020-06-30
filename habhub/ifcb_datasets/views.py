import requests
import csv

from django.shortcuts import render

from .models import *

# Views to access IFCB Dashboard
def _get_ifcb_dataset(dataset_obj):
    response = requests.get(F'https://ifcb-data.whoi.edu/api/export_metadata/{dataset_obj.dashboard_id_name}')
    decoded_content = response.content.decode('utf-8')

    reader = csv.DictReader(decoded_content.splitlines())
    for record in reader:

        obj, created = Bin.objects.get_or_create(
            pid=record['pid'],
            dataset=dataset_obj,
            defaults={'ifcb': record['ifcb'], 'ml_analyzed': record['ml_analyzed']},
        )

        if created:
            print("Record saved")
