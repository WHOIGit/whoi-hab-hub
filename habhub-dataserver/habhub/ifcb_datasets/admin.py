from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin

from .models import *
from .forms import DatasetForm

# Register models here.
class DatasetAdmin(LeafletGeoAdmin):
    form = DatasetForm
    list_display = (
        "name",
        "location",
        "dashboard_base_url",
        "dashboard_id_name",
        "fixed_location",
        "geom",
    )
    list_editable = ("geom",)


class BinAdmin(admin.ModelAdmin):
    search_fields = ["pid"]
    list_display = ("pid", "dataset", "sample_time")
    list_filter = ("dataset",)
    # filter_horizontal = ('shellfish_areas', )


class AutoclassScoreAdmin(admin.ModelAdmin):
    search_fields = ["pid"]
    list_display = ("bin", "pid", "score", "species")
    list_filter = ("species",)


admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Bin, BinAdmin)
admin.site.register(AutoclassScore, AutoclassScoreAdmin)
