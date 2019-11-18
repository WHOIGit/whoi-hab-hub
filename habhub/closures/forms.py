from django import forms
from django.contrib.gis.geos import Point

from .models import Landmark


class LandmarkForm(forms.ModelForm):

    latitude = forms.FloatField(
        min_value=-90,
        max_value=90,
        required=True,
    )
    longitude = forms.FloatField(
        min_value=-180,
        max_value=180,
        required=True,
    )

    class Meta(object):
        model = Landmark
        exclude = []
        fields = ['name', 'state', 'latitude', 'longitude', 'coords' ]
        widgets = {'coords': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        coordinates = self.initial.get('coords', None)
        if isinstance(coordinates, Point):
            self.initial['longitude'], self.initial['latitude'] = coordinates.tuple

    def clean(self):
        data = super().clean()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        coords = data.get('coords')
        if latitude and longitude:
            data['coords'] = Point(longitude, latitude)
        return data
