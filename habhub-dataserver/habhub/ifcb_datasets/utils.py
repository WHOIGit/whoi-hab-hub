import os
import requests
from io import BytesIO

from django.contrib.gis.geos import Polygon
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Bin


"""
Function to make url request to IFCB Dashboard get image if missing locally,
save it to local/AWS storage
Args: 'dataset_obj': Dataset object, 'img_name': string
"""

def get_bins_outside_target_area():
    # create bounding box that covers the North Atlantic
    bbox =  (-81, 25, -47, 49)
    poly = Polygon.from_bbox(bbox)
    print(poly)
    # get all Bins within this cell
    bins = Bin.objects.exclude(geom__within=poly)
    print(bins.count())
    for bin in bins:
        print(bin.geom)

def _get_image_ifcb_dashboard(dataset_obj, img_name):
    image = None
    img_key = f'ifcb/images/{img_name}.png'
    if not default_storage.exists(img_key):
        img_url = f'https://ifcb-data.whoi.edu/{dataset_obj.dashboard_id_name}/{img_name}.png'
        response = requests.get(img_url)
        if response.status_code == 200:
            file = BytesIO()
            file.write(response.content)
            filename = f'{img_name}.png'
            image = default_storage.save(img_key, file)
    return image
