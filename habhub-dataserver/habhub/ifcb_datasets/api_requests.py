import requests
import csv
import datetime
import concurrent.futures
import os
import environ
import decimal
from io import BytesIO

from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.contrib.gis.geos import Point, Polygon

from habhub.core.models import TargetSpecies

env = environ.Env()

IFCB_DASHBOARD_URL = env("IFCB_DASHBOARD_URL", default="https://habon-ifcb.whoi.edu")
IFCB_DASHBOARD_THROTTLE_RATE = env("IFCB_DASHBOARD_THROTTLE_RATE", default=50)


def valid_lonlat(lon: float, lat: float):
    """
    This validates a lat and lon point can be located
    in the bounds of the WGS84 CRS, after wrapping the
    longitude value within [-180, 180)

    :param lon: a longitude value
    :param lat: a latitude value
    :return: (lon, lat) if valid, None otherwise
    """
    # ignore points that are set to 0,0
    if lon == 0 and lat == 0:
        return None

    # Put the longitude in the range of [0,360):
    lon %= 360
    # Put the longitude in the range of [-180,180):
    if lon >= 180:
        lon -= 360
    lon_lat_point = Point(lon, lat)
    bbox = (-180.0, -90.0, 180.0, 90.0)
    lon_lat_bounds = Polygon.from_bbox(bbox)
    # return lon_lat_bounds.intersects(lon_lat_point)
    # would not provide any corrected values

    if lon_lat_bounds.intersects(lon_lat_point):
        return lon, lat
    else:
        return None


# Functions to access IFCB Dashboard
# -------------------------------

"""
def run_species_classifed_import(dataset_obj):
    # Get all new bins
    _get_ifcb_bins_dataset(dataset_obj)
    # Process autoclass files from new IFCB Bins
    # Create a pool of processes. By default, one is created for each CPU on machine.
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Get a list of bins to process
        bins = dataset_obj.bins.filter(cell_concentration_data__isnull=True)[:50]
        #bins = dataset_obj.bins.filter(species_found__isnull=True)[:500]
        # Process the list of bins, but split the work across the process pool
        print("Getting Autoclass files")
        for bin, data in zip(bins, executor.map(_get_ifcb_autoclass_file, bins)):
             print(f"{bin} processed.")
"""


def run_species_classifed_import(dataset_obj):
    """
    Function to run import of Bins/Autoclass/Image data from IFCB dashboard
    Args: 'dataset_obj' - Dataset object
    """
    # Get all new bins
    _get_ifcb_bins_dataset(dataset_obj)
    print("Complete Bin import.")
    bins = dataset_obj.bins.filter(cell_concentration_data__isnull=True)[
        :IFCB_DASHBOARD_THROTTLE_RATE
    ]
    for bin in bins:
        print("Start autoclass processing...")
        _get_ifcb_autoclass_file(bin)
        print(f"{bin} processed.")


def reset_ifcb_data():
    """
    recreate all IFCB data for all Bins in all Datasets
    this operation may take a long time
    """
    from .models import Dataset

    datasets = Dataset.objects.all()
    for dataset in datasets:
        print(f"DATASET: {dataset}")
        # update DB with any new Bins, then delete all existing IFCB data and get new data
        _get_ifcb_bins_dataset(dataset)
        bins = dataset.bins.all()
        for b in bins:
            print()
            print("Start autoclass processing...")
            _get_ifcb_autoclass_file(b)
            print(f"{b} processed.")

    print("Complete all imports.")


def _get_ifcb_bins_dataset(dataset_obj):
    """
    Function to make API request for all IFCB bins by dataset
    Args: 'dataset_obj' - Dataset object
    """
    from .models import Bin

    # get the most recent Bin
    try:
        latest_bin = dataset_obj.bins.latest()
    except Bin.DoesNotExist:
        latest_bin = None

    if latest_bin:
        start_date = latest_bin.sample_time
        params = {"start_date": start_date}
    else:
        params = {}

    csv_url = (
        f"{IFCB_DASHBOARD_URL}/api/export_metadata/{dataset_obj.dashboard_id_name}"
    )

    response = requests.get(csv_url, params=params)
    print(response.status_code, response.url)
    if response.status_code == 200:
        lines = (line.decode("utf-8") for line in response.iter_lines())

        for row in csv.DictReader(lines):
            print(row["pid"])
            # check for valid long/lat. Skip row if no valid geo data
            if row["longitude"] and row["latitude"]:
                lon = float(row["longitude"])
                lat = float(row["latitude"])
                lon_lat = valid_lonlat(lon, lat)

                if lon_lat is None:
                    print("invalid long/lat")
                    continue
                else:
                    lon, lat = lon_lat

                geom = Point(lon, lat)
            else:
                print("no long/lat")
                continue

            sample_time = datetime.datetime.strptime(
                row["sample_time"], "%Y-%m-%d %H:%M:%S%z"
            )

            depth = None
            if row["depth"]:
                depth = row["depth"]

            ml_analyzed = None
            if row["ml_analyzed"] and float(row["ml_analyzed"]) > 0:
                ml_analyzed = row["ml_analyzed"]

            try:
                bin = Bin.objects.create(
                    pid=row["pid"],
                    dataset=dataset_obj,
                    geom=geom,
                    sample_time=row["sample_time"],
                    ifcb=row["ifcb"],
                    ml_analyzed=ml_analyzed,
                    depth=depth,
                    cruise=row["cruise"],
                    cast=row["cast"],
                    niskin=row["niskin"],
                    sample_type=row["sample_type"],
                    n_images=row["n_images"],
                    skip=row["skip"],
                )
                print(f"row saved - {bin.pid}")
            except Exception as e:
                print(e)


def _get_ifcb_autoclass_file(bin_obj):
    """
    Function to make API request for Autoclass CSV file, calculate abundance of target species
    Args: 'dataset_obj' - Dataset object, 'bin_obj' -  Bin object
    """
    bin_url = f"{IFCB_DASHBOARD_URL}/bin?dataset={bin_obj.dataset.dashboard_id_name}&bin={bin_obj.pid}"
    class_scores_url = f"{IFCB_DASHBOARD_URL}/{bin_obj.dataset.dashboard_id_name}/{bin_obj.pid}_class_scores.csv"
    features_url = f"{IFCB_DASHBOARD_URL}/{bin_obj.dataset.dashboard_id_name}/{bin_obj.pid}_features.csv"
    ml_analyzed = bin_obj.ml_analyzed

    target_list = TargetSpecies.objects.values_list("species_id", flat=True)
    print(f"DASHBOARD URL requested: {bin_url}")
    species_found = []
    # set up data structure to store results
    data = []
    for species in target_list:
        dict = {
            "species": species,
            "image_count": 0,
            "cell_concentration": 0,
            "biovolume": 0,
            "image_numbers": [],
        }
        data.append(dict)

    # get the autoclass CSV to calculate cell concentrations. This is required
    try:
        response = requests.get(class_scores_url, timeout=1)
    except Exception as e:
        print(e)
        return data

    # get the features csv to calculate Biovolumes. Continue if unavailable
    try:
        response_features = requests.get(features_url, timeout=1)
    except Exception as e:
        print(e)
        response_features = None
        pass

    # debug print if we features.csv exists:
    if response_features and response_features.status_code == 200:
        print(f"FEATURES URL: {features_url}")
    else:
        print(f"NO FEATURES CSV FOUND: 404 - {features_url}")

    if response.status_code == 200:
        lines = (line.decode("utf-8") for line in response.iter_lines())
        for row in csv.DictReader(lines):
            # remove the pid column
            image_number = row["pid"]
            row.pop("pid", None)
            # get the item with the highest value, return species name in key
            species = max(row, key=lambda key: float(row[key]))
            # get the value for that species
            max_val = row[species]
            # print(max_val)
            if species in target_list:
                species_found.append(species)
                # increment the abundance count by 1 if species matches a TargetSpecies
                item = next(
                    (item for item in data if item["species"] == species), False
                )
                item["image_count"] += 1
                item["image_numbers"].append(image_number)

        for item in data:
            try:
                # calculate cell concentrations
                # number of positive hits (image_count) / mL analyed.
                # multiply by 1000 to convert to per L
                item["cell_concentration"] = int(
                    round((item["image_count"] / ml_analyzed) * 1000)
                )
                # calculate Biovolume
                # There are ~2.77 pixels per micron so to convert voxel biovolume
                # to cubic microns divide values by 2.77^3 or 21.254
                ####
                # Calculate the sum of biovolumes / volume analyzed by class.
                # So, e.g. sum of all biovolumes from images identified as cylindrospermopsis (or any other class)
                # divided by the volume analyzed (some number of mL between 0 and 5).
                if response_features and response_features.status_code == 200:
                    print("FEATURE CSV LOADED", response_features.status_code)
                    # need to reduce image_number string to last 5 numbers, then strip zeroes
                    image_ids = item["image_numbers"]
                    biovolume_total = 0
                    image_ids = [img[-5:].lstrip("0") for img in image_ids]
                    # print(image_ids)
                    lines = (
                        line.decode("utf-8") for line in response_features.iter_lines()
                    )
                    for row in csv.DictReader(lines):

                        if row["roi_number"] in image_ids:
                            # convert to cubic microns
                            biovolume = float(row["Biovolume"]) / 21.254
                            biovolume_total = biovolume_total + biovolume

                    biovolume_final = int(
                        round((biovolume_total / float(ml_analyzed)) * 1000)
                    )
                    item["biovolume"] = biovolume_final
                # remove duplications from species_found list
                species_found = list(set(species_found))
            except Exception as e:
                print(e)
                pass

        # update Bin record
        print(f"Data for {bin_obj}: {data}")
        bin_obj.cell_concentration_data = data
        bin_obj.species_found = species_found
        bin_obj.save()
    return data
