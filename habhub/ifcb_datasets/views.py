import requests
import csv
import datetime

from django.shortcuts import render
from django.contrib.gis.geos import Point

from .models import *

# Views to access IFCB Dashboard
# -------------------------------
"""
Function to make API request for all IFCB bins by dataset
Args: 'dataset_obj' - Dataset object
"""
def _get_ifcb_dataset(dataset_obj):
    response = requests.get(F'https://ifcb-data.whoi.edu/api/export_metadata/{dataset_obj.dashboard_id_name}')
    decoded_content = response.content.decode('utf-8')
    reader = csv.DictReader(decoded_content.splitlines())
    # speed up the process by getting a values list of current Bin pid
    bins = Bin.objects.filter(dataset=dataset_obj).values('pid')
    for record in reader:
        if record['pid'] not in [bin['pid'] for bin in bins]:
            sample_time = datetime.datetime.strptime(record['sample_time'], "%Y-%m-%d %H:%M:%S%z")
            geom = None
            if record['longitude'] and record['latitude']:
                print(record['longitude'])
                geom = Point(float(record['longitude']), float(record['latitude']))

            bin = Bin.objects.create(
                pid = record['pid'],
                dataset = dataset_obj,
                geom = geom,
                sample_time = record['sample_time'],
                ifcb = record['ifcb'],
                ml_analyzed = record['ml_analyzed'],
                depth = record['depth'],
                cruise = record['cruise'],
                cast = record['cast'],
                niskin = record['niskin'],
                sample_type = record['sample_type'],
                n_images = record['n_images'],
                skip = record['skip'],
            )
            print("Record saved")
