import os
import requests
from io import BytesIO
import s2sphere

from django.contrib.gis.geos import Polygon
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Bin, GeohashGrid
from .constants import geojson_atlantic


def convert_s2_point_to_latlng(s2_point):
    # utility function to convert S2 points to lat/lng
    coords = str(s2_point).split()[-1].split(",")
    lat_lng = {"lat": float(coords[0]), "long": float(coords[1])}
    return lat_lng


def create_region_geohash_grid():
    """
    Function to create base geohash grids for different coastal regions.
    Grids are saved in DB table and used to preaggregate geospatial binned data
    """
    for feature in geojson_atlantic["features"]:
        bbox = feature["geometry"]["coordinates"][0]
        region = feature["properties"]["region"]
        s2_grid_level = 7
        # S2 functions to get even grid of polygons to cover region bounding box
        r = s2sphere.RegionCoverer()
        r.min_level = s2_grid_level
        r.max_level = s2_grid_level
        p1 = s2sphere.LatLng.from_degrees(bbox[0][1], bbox[0][0])
        p2 = s2sphere.LatLng.from_degrees(bbox[2][1], bbox[2][0])
        print(p1)
        print(p2)
        covering = r.get_covering(s2sphere.LatLngRect.from_point_pair(p1, p2))
        for cellid in covering:
            cell_center_ll = cellid.to_lat_lng()
            lat_lng = convert_s2_point_to_latlng(cell_center_ll)
            geohash_token = cellid.to_token()
            print(geohash_token)
            geohash_grid = GeohashGrid(
                geohash_token=geohash_token, s2_grid_level=s2_grid_level, region=region
            )
            print(geohash_grid)
            geohash_grid.save()


def get_bins_outside_target_area():
    # create bounding box that covers the North Atlantic
    bbox = (-81, 25, -47, 49)
    poly = Polygon.from_bbox(bbox)
    print(poly)
    # get all Bins within this cell
    bins = Bin.objects.exclude(geom__within=poly)
    print(bins.count())
    for bin in bins:
        print(bin.geom)


def _get_image_ifcb_dashboard(dataset_obj, img_name):
    """
    Function to make url request to IFCB Dashboard get image if missing locally,
    save it to local/AWS storage
    Args: 'dataset_obj': Dataset object, 'img_name': string
    """
    image = None
    img_key = f"ifcb/images/{img_name}.png"
    if not default_storage.exists(img_key):
        img_url = (
            f"https://ifcb-data.whoi.edu/{dataset_obj.dashboard_id_name}/{img_name}.png"
        )
        response = requests.get(img_url)
        if response.status_code == 200:
            file = BytesIO()
            file.write(response.content)
            filename = f"{img_name}.png"
            image = default_storage.save(img_key, file)
    return image
