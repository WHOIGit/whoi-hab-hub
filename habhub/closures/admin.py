from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin

from .models import ClosureArea, Species, ClosureNotice, CausativeOrganism, ShellfishArea

# Register your models here.

class ShellfishAreaAdmin(LeafletGeoAdmin):
    ordering = ['name']
    search_fields = ['name']


class ClosureAreaAdmin(LeafletGeoAdmin):
    ordering = ['name']
    search_fields = ['name']


class ClosureNoticeAdmin(LeafletGeoAdmin):
    #autocomplete_fields = ['closure_areas']
    pass


admin.site.register(ShellfishArea, ShellfishAreaAdmin)

admin.site.register(ClosureArea, ClosureAreaAdmin)

admin.site.register(ClosureNotice, ClosureNoticeAdmin)

admin.site.register(Species)

admin.site.register(CausativeOrganism)
