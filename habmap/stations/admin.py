from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Station, Datapoint

# Register your models here.

@admin.register(Station)
class StationAdmin(ImportExportModelAdmin):
    pass

@admin.register(Datapoint)
class DatapointAdmin(ImportExportModelAdmin):
    pass

class StationResource(resources.ModelResource):

    class Meta:
        model = Station

class DatapointResource(resources.ModelResource):

    class Meta:
        model = Datapoint        
