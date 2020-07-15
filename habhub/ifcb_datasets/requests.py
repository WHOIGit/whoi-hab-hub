import requests
import csv
import datetime

from django.shortcuts import render
from django.contrib.gis.geos import Point

from .models import *

# Views to access IFCB Dashboard
# -------------------------------

"""
Function to make API request for Autoclass CSV file, calculate abundance of target species
Args: 'dataset_obj' - Dataset object, 'bin_obj' -  Bin object
"""
def _get_ifcb_autoclass_file(dataset_obj=None, bin_obj=None):
    CSV_URL = 'https://ifcb-data.whoi.edu/fiddlers/D20200630T132819_IFCB124_class_scores.csv'
    TARGET_SPECIES = [
        'Alexandrium_catenella',
        'Dinophysis',
        'Dinophysis_acuminata',
        'Dinophysis_norvegica',
    ]

    target_species_found = False
    # set up data structure to store results
    data = []
    for species in TARGET_SPECIES:
        dict = {'species': species, 'image_count': 0, 'concentration': 0, 'image_numbers': []}
        data.append(dict)

    with requests.get(CSV_URL, stream=True) as response:
        lines = (line.decode('utf-8') for line in response.iter_lines())
        for row in csv.DictReader(lines):
            # remove the pid column
            image_number = row['pid']
            row.pop('pid', None)
            # get the item with the highest value, return species name in key
            species = max(row, key=lambda key: float(row[key]))
            if species in TARGET_SPECIES:
                print(species)
                target_species_found = True
                # increment the abundance count by 1 if species matches a TARGET_SPECIES
                item = next((item for item in data if item['species'] == species), False)
                item['image_count'] += 1
                item['image_numbers'].append(image_number)
    print(data)
    if response.status_code == 200:
        print(response.status_code)


"""
Function to make API request for all IFCB bins by dataset
Args: 'dataset_obj' - Dataset object
"""
def _get_ifcb_dataset(dataset_obj):
    CSV_URL = F'https://ifcb-data.whoi.edu/api/export_metadata/{dataset_obj.dashboard_id_name}'
    # speed up the process by getting a values list of current Bin pid
    bins = Bin.objects.filter(dataset=dataset_obj).values('pid')

    with requests.get(CSV_URL, stream=True) as response:
        lines = (line.decode('utf-8') for line in response.iter_lines())
        for row in csv.DictReader(lines):
            if row['pid'] not in [bin['pid'] for bin in bins]:
                sample_time = datetime.datetime.strptime(row['sample_time'], "%Y-%m-%d %H:%M:%S%z")
                geom = None
                if row['longitude'] and row['latitude']:
                    geom = Point(float(row['longitude']), float(row['latitude']))

                bin = Bin.objects.create(
                    pid = row['pid'],
                    dataset = dataset_obj,
                    geom = geom,
                    sample_time = row['sample_time'],
                    ifcb = row['ifcb'],
                    ml_analyzed = row['ml_analyzed'],
                    depth = row['depth'],
                    cruise = row['cruise'],
                    cast = row['cast'],
                    niskin = row['niskin'],
                    sample_type = row['sample_type'],
                    n_images = row['n_images'],
                    skip = row['skip'],
                )
                print(F"row saved - {bin.pid}")
