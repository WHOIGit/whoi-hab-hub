import requests
import csv
import datetime
import concurrent.futures
import os
from io import BytesIO

from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.contrib.gis.geos import Point

from .models import *

# Functions to access IFCB Dashboard
# -------------------------------

"""
Function to run import of Bins/Autoclass/Image data from IFCB dashboard
Args: 'dataset_obj' - Dataset object
"""
def run_species_classifed_import(dataset_obj):
    # Get all new bins
    _get_ifcb_bins_dataset(dataset_obj)
    # Process autoclass files from new IFCB Bins
    # Create a pool of processes. By default, one is created for each CPU on machine.
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Get a list of bins to process
        bins = dataset_obj.bins.filter(cell_concentration_data__isnull=True)[:500]
        #bins = dataset_obj.bins.filter(species_found__isnull=True)[:500]
        print(bins)
        # Process the list of bins, but split the work across the process pool
        for bin, data in zip(bins, executor.map(_get_ifcb_autoclass_file, bins)):
             print(f"{bin} processed.")
    # Get most recent images of each target species after data processing
    _get_most_recent_images(dataset_obj)


"""
Function to make API request for all IFCB bins by dataset
Args: 'dataset_obj' - Dataset object
"""
def _get_ifcb_bins_dataset(dataset_obj):
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
                depth = None
                if row['depth']:
                    depth = row['depth']

                bin = Bin.objects.create(
                    pid = row['pid'],
                    dataset = dataset_obj,
                    geom = geom,
                    sample_time = row['sample_time'],
                    ifcb = row['ifcb'],
                    ml_analyzed = row['ml_analyzed'],
                    depth = depth,
                    cruise = row['cruise'],
                    cast = row['cast'],
                    niskin = row['niskin'],
                    sample_type = row['sample_type'],
                    n_images = row['n_images'],
                    skip = row['skip'],
                )
                print(F"row saved - {bin.pid}")


"""
Function to make API request for Autoclass CSV file, calculate abundance of target species
Args: 'dataset_obj' - Dataset object, 'bin_obj' -  Bin object
"""
def _get_ifcb_autoclass_file(bin_obj):
    CSV_URL = F'https://ifcb-data.whoi.edu/{bin_obj.dataset.dashboard_id_name}/{bin_obj.pid}_class_scores.csv'
    ML_ANALYZED = bin_obj.ml_analyzed
    TARGET_SPECIES = [species[0] for species in Bin.TARGET_SPECIES]

    species_found = []
    # set up data structure to store results
    data = []
    for species in TARGET_SPECIES:
        dict = {'species': species, 'image_count': 0, 'cell_concentration': 0, 'image_numbers': []}
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
                species_found.append(species)
                # increment the abundance count by 1 if species matches a TARGET_SPECIES
                item = next((item for item in data if item['species'] == species), False)
                item['image_count'] += 1
                item['image_numbers'].append(image_number)

    if response.status_code == 200:
        for row in data:
            try:
                # calculate cell concentrations
                row['cell_concentration'] = int(round((row['image_count'] / ML_ANALYZED) * 1000))
                # remove duplications from species_found list
                species_found = list(set(species_found))
            except Exception as e:
                print(e)

        #update Bin record
        bin_obj.cell_concentration_data = data
        bin_obj.species_found = species_found
        bin_obj.save()
    return data


"""
Function to make url request to get most recent image of each target species
Args: 'dataset_obj' - Dataset object
"""
def _get_most_recent_images(dataset_obj):
    TARGET_SPECIES = Bin.TARGET_SPECIES
    for species in TARGET_SPECIES:
        latest_bin = dataset_obj.bins.filter(species_found__contains=[species[0]]).latest()
        data = latest_bin.get_concentration_data_by_species(species[0])
        img_name = data['image_numbers'][0]

        if not os.path.isfile(os.path.join(settings.MEDIA_ROOT , F'ifcb/images/{img_name}.png')):
            img_url = F'https://ifcb-data.whoi.edu/{dataset_obj.dashboard_id_name}/{img_name}.png'
            print(img_url)
            response = requests.get(img_url)
            if response.status_code == 200:
                file = BytesIO()
                file.write(response.content)
                filename = F'{img_name}.png'
                image = default_storage.save('ifcb/images/' + filename, file)
                print(image)
        else:
            print('image exists')
