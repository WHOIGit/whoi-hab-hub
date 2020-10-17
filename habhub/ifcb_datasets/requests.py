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
"""
def run_species_classifed_import(dataset_obj):
    # Get all new bins
    _get_ifcb_bins_dataset(dataset_obj)
    # Process autoclass files from new IFCB Bins
    # Create a pool of processes. By default, one is created for each CPU on machine.
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Get a list of bins to process
        bins = dataset_obj.bins.filter(cell_concentration_data__isnull=True)[:200]
        #bins = dataset_obj.bins.filter(species_found__isnull=True)[:500]
        # Process the list of bins, but split the work across the process pool
        print("Getting Autoclass files")
        for bin, data in zip(bins, executor.map(_get_ifcb_autoclass_file, bins)):
             print(f"{bin} processed.")
"""
def run_species_classifed_import(dataset_obj):
    # Get all new bins
    _get_ifcb_bins_dataset(dataset_obj)
    bins = dataset_obj.bins.filter(cell_concentration_data__isnull=True)[:100]
    for bin in bins:
        _get_ifcb_autoclass_file(bin)
        print(f"{bin} processed.")

"""
Function to make API request for all IFCB bins by dataset
Args: 'dataset_obj' - Dataset object
"""
def _get_ifcb_bins_dataset(dataset_obj):
    CSV_URL = F'https://ifcb-data.whoi.edu/api/export_metadata/{dataset_obj.dashboard_id_name}'
    # speed up the process by getting a values list of current Bin pid
    bins = Bin.objects.filter(dataset=dataset_obj).values_list('pid', flat=True)
    print('Bins:', bins.count())
    # MVCO dataset has old formats that don't play well with HABHub, skip older bins
    mvco_check = True
    if dataset_obj.dashboard_id_name == 'mvco':
        mvco_check = False

    response = requests.get(CSV_URL)
    print(response.status_code)
    if response.status_code == 200:
        lines = (line.decode('utf-8') for line in response.iter_lines())
        #row = next((row for row in csv.DictReader(lines) if row['pid'] not in bins), False)
        for row in csv.DictReader(lines):
            if mvco_check == False:
                if 'IFCB1' not in row['pid']:
                    mvco_check = True

            if row['pid'] not in bins and mvco_check == True:
                print(row['pid'])
                sample_time = datetime.datetime.strptime(row['sample_time'], "%Y-%m-%d %H:%M:%S%z")

                geom = None
                if row['longitude'] and row['latitude']:
                    geom = Point(float(row['longitude']), float(row['latitude']))

                depth = None
                if row['depth']:
                    depth = row['depth']

                ml_analyzed = None
                if row['ml_analyzed'] and float(row['ml_analyzed'])  > 0:
                    ml_analyzed = row['ml_analyzed']

                try:
                    bin = Bin.objects.create(
                        pid = row['pid'],
                        dataset = dataset_obj,
                        geom = geom,
                        sample_time = row['sample_time'],
                        ifcb = row['ifcb'],
                        ml_analyzed = ml_analyzed,
                        depth = depth,
                        cruise = row['cruise'],
                        cast = row['cast'],
                        niskin = row['niskin'],
                        sample_type = row['sample_type'],
                        n_images = row['n_images'],
                        skip = row['skip'],
                    )
                    print(F"row saved - {bin.pid}")
                except Exception as e:
                    print(e)


"""
Function to make API request for Autoclass CSV file, calculate abundance of target species
Args: 'dataset_obj' - Dataset object, 'bin_obj' -  Bin object
"""
def _get_ifcb_autoclass_file(bin_obj):
    CSV_URL = F'https://ifcb-data.whoi.edu/{bin_obj.dataset.dashboard_id_name}/{bin_obj.pid}_class_scores.csv'
    ML_ANALYZED = bin_obj.ml_analyzed
    TARGET_SPECIES = [species[0] for species in Bin.TARGET_SPECIES]
    print(CSV_URL, bin_obj)
    species_found = []
    # set up data structure to store results
    data = []
    for species in TARGET_SPECIES:
        dict = {'species': species, 'image_count': 0, 'cell_concentration': 0, 'image_numbers': []}
        data.append(dict)

    response = requests.get(CSV_URL)
    print(response.status_code)
    if response.status_code == 200:
        lines = (line.decode('utf-8') for line in response.iter_lines())
        for row in csv.DictReader(lines):
            print("reading autoclass data")
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
            print("calculate concentration")
            try:
                # calculate cell concentrations
                row['cell_concentration'] = int(round((row['image_count'] / ML_ANALYZED) * 1000))
                # remove duplications from species_found list
                species_found = list(set(species_found))
            except Exception as e:
                print(e)

        #update Bin record
        print("save to DB")
        bin_obj.cell_concentration_data = data
        bin_obj.species_found = species_found
        bin_obj.save()
    return data
