from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from .models import Cruise, IFCBDatapoint

# Register models here.

admin.site.register(Cruise)

@admin.register(IFCBDatapoint)
class IFCBDatapointAdmin(ImportExportModelAdmin):
    pass

class IFCBDatapointResource(resources.ModelResource):

    class Meta:
        model = IFCBDatapoint
