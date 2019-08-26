from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import ClosureArea

# Register your models here.

admin.site.register(ClosureArea, LeafletGeoAdmin)
