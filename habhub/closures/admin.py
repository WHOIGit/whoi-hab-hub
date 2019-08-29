from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import ClosureArea, Species, ClosureNotice

# Register your models here.

class ClosureAreaAdmin(LeafletGeoAdmin):
    ordering = ['name']
    search_fields = ['name']

class ClosureNoticeAdmin(admin.ModelAdmin):
    autocomplete_fields = ['closure_areas']

admin.site.register(ClosureArea, ClosureAreaAdmin)

admin.site.register(ClosureNotice, ClosureNoticeAdmin)

admin.site.register(Species)
