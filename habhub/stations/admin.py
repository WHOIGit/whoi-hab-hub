from django.contrib.gis import admin
from django.contrib.gis.geos import Point

from leaflet.admin import LeafletGeoAdmin, LeafletGeoAdminMixin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from import_export.fields import Field

from .models import Station, Datapoint
from .forms import StationForm

# Resource class for import_export module
class StationResource(resources.ModelResource):
    latitude = Field(attribute='latitude', column_name='latitude')
    longitude = Field(attribute='longitude', column_name='longitude')

    class Meta:
        model = Station
        fields = ('id', 'station_name', 'station_location', 'state', 'latitude', 'longitude')
        exclude = ('geom', 'hab_species')
        export_order = ('id', 'station_name', 'station_location', 'state', 'latitude', 'longitude')

    def before_save_instance(self, instance, using_transactions, dry_run):
        # convert lat/long into GeoDjango Point
        instance.geom = Point(float(instance.longitude), float(instance.latitude))
        # convert state names to IDs
        if instance.state == 'Maine':
            instance.state = 'ME'
        elif instance.state == 'Massachusetts':
            instance.state = 'MA'
        elif instance.state == 'New Hampshire':
            instance.state = 'NH'

        return instance


@admin.register(Station)
class StationAdmin(LeafletGeoAdminMixin, ImportExportModelAdmin):
    form = StationForm
    resource_class = StationResource
    list_display = ('station_name', 'station_location', 'state', 'geom')
    list_editable = ('geom', )
    list_filter = ('state',)


# Resource class for import_export module
class DatapointResource(resources.ModelResource):
    class Meta:
        model = Datapoint


@admin.register(Datapoint)
class DatapointAdmin(ImportExportModelAdmin):
    resource_class = DatapointResource
