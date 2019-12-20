from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from .models import MonitoringSystem
from .forms import MonitoringSystemForm

# Register your models here.

@admin.register(MonitoringSystem)
class MonitoringSystemAdmin(ImportExportModelAdmin):
    form = MonitoringSystemForm
