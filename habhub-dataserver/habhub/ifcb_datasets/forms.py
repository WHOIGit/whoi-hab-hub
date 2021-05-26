from django import forms
from django.contrib.gis.geos import Point

from .models import Dataset

class DatasetForm(forms.ModelForm):

    latitude = forms.FloatField(
        min_value=-90,
        max_value=90,
        required=False,
    )
    longitude = forms.FloatField(
        min_value=-180,
        max_value=180,
        required=False,
    )

    class Meta(object):
        model = Dataset
        fields = ['name', 'location', 'dashboard_id_name', 'fixed_location', 'latitude', 'longitude', 'geom', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        coordinates = self.initial.get('geom', None)
        if isinstance(coordinates, Point):
            self.initial['longitude'], self.initial['latitude'] = coordinates.tuple

    def clean(self):
        data = super().clean()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        geom = data.get('geom')
        if latitude and longitude:
            data['geom'] = Point(longitude, latitude)
        return data
