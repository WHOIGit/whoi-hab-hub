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

from habhub.core.constants import METRICS

env = environ.Env()

# IFCB_DASHBOARD_URL = env("IFCB_DASHBOARD_URL", default="https://habon-ifcb.whoi.edu")
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
        print("Start calculating metrics from scores..")
        _calculate_metrics(bin)
        print(f"{bin} processed.")
        _calculate_aggregates(bin)
        print(f"{bin} aggregate data saved.")


def reset_ifcb_data(dataset_id=None):
    """
    recreate all IFCB data for all Bins in all Datasets or single Dataset
    this operation may take a long time
    """
    from .models import Dataset

    print("REQUEST DATASET ID ", dataset_id)

    if not dataset_id:
        datasets = Dataset.objects.all()
        for dataset in datasets:
            print(f"DATASET: {dataset}")
            # update DB with any new Bins, then replace all existing IFCB data
            _get_ifcb_bins_dataset(dataset)
            bins = dataset.bins.all()
            for bin in bins:
                print("Start autoclass processing...")
                _get_ifcb_autoclass_file(bin)
                print("Start calculating metrics from scores..")
                _calculate_metrics(bin)
                print(f"{bin} processed.")
                _calculate_aggregates(bin)
                print(f"{bin} aggregate data saved.")
    else:
        dataset_obj = Dataset.objects.get(id=dataset_id)
        # update DB with any new Bins, then replace all existing IFCB data
        _get_ifcb_bins_dataset(dataset_obj)
        bins = dataset_obj.bins.all()
        for bin in bins:
            print("Start autoclass processing...")
            _get_ifcb_autoclass_file(bin)
            print("Start calculating metrics from scores..")
            _calculate_metrics(bin)
            print(f"{bin} processed.")
            _calculate_aggregates(bin)
            print(f"{bin} aggregate data saved.")
    print("Complete data ingestion.")


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

    csv_url = f"{dataset_obj.dashboard_base_url}/api/export_metadata/{dataset_obj.dashboard_id_name}"

    response = requests.get(csv_url, params=params)
    print(response.status_code, response.url)
    if response.status_code == 200:
        lines = (line.decode("utf-8") for line in response.iter_lines())

        for row in csv.DictReader(lines):
            print(row["pid"])
            # check if "skip" value is true
            # check for valid long/lat. Skip row if no valid geo data
            if row["skip"] == 1:
                print("Skip value set to 1, skipping row")
                continue

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
    from habhub.core.models import TargetSpecies
    from .models import AutoclassScore

    bin_url = f"{bin_obj.dataset.dashboard_base_url}/bin?dataset={bin_obj.dataset.dashboard_id_name}&bin={bin_obj.pid}"
    class_scores_url = f"{bin_obj.dataset.dashboard_base_url}/{bin_obj.dataset.dashboard_id_name}/{bin_obj.pid}_class_scores.csv"

    target_list = TargetSpecies.objects.values_list("species_id", flat=True)
    print(f"DASHBOARD URL requested: {bin_url} {class_scores_url}")

    # get the autoclass CSV to calculate cell concentrations. This is required
    try:
        response = requests.get(class_scores_url, timeout=2)
    except Exception as e:
        print(e)
        return

    print(f"Response code: {response.status_code}")
    if response.status_code == 200:
        lines = (line.decode("utf-8") for line in response.iter_lines())
        for row in csv.DictReader(lines):
            # remove the pid column
            image_number = row["pid"]
            row.pop("pid", None)
            # get the item with the highest value, return species name in key
            species = max(row, key=lambda key: float(row[key]))

            if species in target_list:
                # get the value for that species
                max_val = row[species]
                species_obj = TargetSpecies.objects.get(species_id=species)
                # create autoclass score object for this Bin/Species
                autoclass_score, created = AutoclassScore.objects.update_or_create(
                    pid=image_number,
                    defaults={"score": max_val, "species": species_obj, "bin": bin_obj},
                )
                # print(autoclass_score.score, autoclass_score.species)


def _calculate_metrics(bin_obj):
    from habhub.core.models import TargetSpecies

    features_url = f"{bin_obj.dataset.dashboard_base_url}/{bin_obj.dataset.dashboard_id_name}/{bin_obj.pid}_features.csv"
    ml_analyzed = bin_obj.ml_analyzed
    target_list = TargetSpecies.objects.all()

    # get the features csv to calculate Biovolumes. Continue if unavailable
    try:
        response_features = requests.get(features_url, timeout=2)
    except Exception as e:
        print(e)
        response_features = None
        pass

    # set up data structure to store results
    data = []
    species_found = []

    for species in target_list:
        item_dict = {
            "species": species.species_id,
            "image_count": 0,
            "cell_concentration": 0,
            "biovolume": 0,
            "image_numbers": [],
        }

        # check if species was found regardless of threshold value,
        # save on bin_obj for easier lookups
        is_species_found = bin_obj.autoclass_scores.filter(species=species).exists()

        if is_species_found:
            species_found.append(species.species_id)

        # now find all scores that are greater than/equal to threshold value
        scores = bin_obj.autoclass_scores.filter(species=species).filter(
            score__gte=species.autoclass_threshold
        )

        # print(species.species_id, scores.count())
        if scores.exists():
            # calculate cell concentrations
            # number of positive hits (score_count) / mL analyed.
            # multiply by 1000 to convert to per L
            item_dict["cell_concentration"] = int(
                round((scores.count() / ml_analyzed) * 1000)
            )
            for score in scores:
                item_dict["image_numbers"].append(score.pid)

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
                image_ids = item_dict["image_numbers"]
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
                item_dict["biovolume"] = biovolume_final

        data.append(item_dict)

    # update Bin record
    # print(f"Data for {bin_obj}: {data}, {species_found}")
    bin_obj.species_found = species_found
    bin_obj.cell_concentration_data = data
    bin_obj.save()


def _calculate_aggregates(bin):
    from .models import AggregateDatasetMetric

    print("CALCULATING DAILY AGGREGATES")
    # Function to preprocess aggregate data as new bins are added
    bin_day = bin.sample_time.date()
    print(bin_day)
    agg_bin_daily = AggregateDatasetMetric.objects.filter(sample_time=bin_day).filter(
        timespan="Daily"
    )
    print(agg_bin_daily)
    new_metrics = []

    if not agg_bin_daily:
        # no daily aggregate, create new one
        # setup metric JSON

        for item in bin.cell_concentration_data:
            print(item)
            agg_data = {"species": item["species"], "data": []}
            biovolume_data = {
                "metricId": "biovolume",
                "metricName": "Biovolume",
                "maxValue": item["biovolume"],
                "meanValue": item["biovolume"],
                "units": "cubic microns/L",
            }
            cell_concentration_data = {
                "metricId": "cell_concentration",
                "metricName": "Cell Concentration",
                "maxValue": item["cell_concentration"],
                "meanValue": item["cell_concentration"],
                "units": "cells/L",
            }
            agg_data["data"].append(biovolume_data)
            agg_data["data"].append(cell_concentration_data)
            new_metrics.append(agg_data)

        new_bin = AggregateDatasetMetric(
            sample_time=bin_day,
            timespan="Daily",
            dataset=bin.dataset,
            metrics=new_metrics,
            count=1,
        )
        new_bin.save()
    else:
        # update aggregate data
        agg_bin_daily_obj = agg_bin_daily[0]
        print("Current metrics:", agg_bin_daily_obj.metrics)
        for item in bin.cell_concentration_data:
            for agg_item in agg_bin_daily_obj.metrics:
                if item["species"] == agg_item["species"]:
                    print(f"update daily agg for {agg_item['species']}")
                    agg_data = {"species": item["species"], "data": []}

                    # update biovolume values
                    current_biovolume = [
                        metric
                        for metric in agg_item["data"]
                        if metric["metricId"] == "biovolume"
                    ][0]

                    new_max = current_biovolume["maxValue"]
                    if item["biovolume"] > current_biovolume["maxValue"]:
                        new_max = item["biovolume"]

                    new_mean = (
                        current_biovolume["meanValue"] + item["biovolume"]
                    ) / agg_bin_daily_obj.count

                    biovolume_data = {
                        "metricId": "biovolume",
                        "metricName": "Biovolume",
                        "maxValue": new_max,
                        "meanValue": new_mean,
                        "units": "cubic microns/L",
                    }

                    # update cell concentration values
                    current_concentration = [
                        metric
                        for metric in agg_item["data"]
                        if metric["metricId"] == "cell_concentration"
                    ][0]

                    new_max = current_concentration["maxValue"]
                    if item["cell_concentration"] > current_concentration["maxValue"]:
                        new_max = item["cell_concentration"]

                    new_mean = (
                        current_concentration["meanValue"] + item["cell_concentration"]
                    ) / agg_bin_daily_obj.count

                    cell_concentration_data = {
                        "metricId": "cell_concentration",
                        "metricName": "Cell Concentration",
                        "maxValue": new_max,
                        "meanValue": new_mean,
                        "units": "cells/L",
                    }

                    agg_data["data"].append(biovolume_data)
                    agg_data["data"].append(cell_concentration_data)
                    new_metrics.append(agg_data)

        agg_bin_daily_obj.metrics = new_metrics
        agg_bin_daily_obj.count = agg_bin_daily_obj.count + 1
        agg_bin_daily_obj.save()
