from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from .models import EspInstrument, Deployment, EspDatapoint

# Register your models here.

admin.site.register(EspInstrument)

admin.site.register(Deployment)

@admin.register(EspDatapoint)
class EspDatapointAdmin(ImportExportModelAdmin):
    pass

class EspDatapointResource(resources.ModelResource):

    class Meta:
        model = EspDatapoint
