from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin

from .models import *
from .forms import DatasetForm

# Register models here.
class DatasetAdmin(LeafletGeoAdmin):
    form = DatasetForm
    list_display = ('name', 'location', 'dashboard_id_name', 'fixed_location', 'geom')
    list_editable = ('geom', )

admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Bin)
