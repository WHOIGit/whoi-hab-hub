import json
import requests

from django.templatetags.static import static
from django.contrib.sites.models import Site
from django.db.models import Count
from django.contrib.gis.geos import MultiPolygon, Polygon

from .models import *

"""
Utility functions for the closures app
"""

# Import functions for NH Shellfish Areas
def import_shellfisharea_json_nh():
    domain = Site.objects.get_current().domain
    path = static('json/nh-shellfish-areas.json')

    target_url = 'https://{domain}{path}'.format(domain=domain, path=path)
    response = requests.get(target_url, verify=False)
    data = response.json()

    for feature in data['features']:
        print(feature['properties']['NAME'])
        print(feature['properties']['ATLAS_KEY'])
        try:
            area = ShellfishArea.objects.get(name=feature['properties']['NAME'])
        except ShellfishArea.DoesNotExist:
            area = None

        print(area)

        if area:
            area.atlas_key = feature['properties']['ATLAS_KEY']
            area.save()


# Create new ShellfishArea by combining all areas that share 'atlas_key' for NH
def create_shellfisharea_groupby_atlas():
    areas = ShellfishArea.objects.filter(state="NH").exclude(atlas_key__exact='').order_by('atlas_key')
    keys = areas.values('atlas_key').annotate(acount=Count('atlas_key'))

    for key in keys:
        print(key)
        sub_areas = ShellfishArea.objects.filter(atlas_key=key['atlas_key'])

        combined_area = MultiPolygon()
        for area in sub_areas:
            combined_area = combined_area.union(area.geom)

        if isinstance(combined_area, Polygon):
            combined_area = MultiPolygon(combined_area)

        new_area = ShellfishArea.objects.create(name=key['atlas_key'],
                                                atlas_key=key['atlas_key'],
                                                state='NH',
                                                geom=combined_area,
                                                is_atlas_combined_area=True)
