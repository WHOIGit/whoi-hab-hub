from django.contrib.gis import admin

from leaflet.admin import LeafletGeoAdmin, LeafletGeoAdminMixin
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from .models import Station, Datapoint, Species
from .forms import StationForm

# Register your models here.

admin.site.register(Species)

@admin.register(Station)
class StationAdmin(LeafletGeoAdminMixin, ImportExportModelAdmin):
    form = StationForm
    list_display = ('station_name', 'station_location', 'state', 'geom')
    list_editable = ('geom', )
    list_filter = ('state',)

@admin.register(Datapoint)
class DatapointAdmin(ImportExportModelAdmin):
    pass

class StationResource(resources.ModelResource):

    class Meta:
        model = Station

class DatapointResource(resources.ModelResource):

    class Meta:
        model = Datapoint
