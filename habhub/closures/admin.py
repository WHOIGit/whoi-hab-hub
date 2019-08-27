from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import ClosureArea, Species, ClosureNotice

# Register your models here.

admin.site.register(ClosureArea, LeafletGeoAdmin)

admin.site.register(Species)

admin.site.register(ClosureNotice)
