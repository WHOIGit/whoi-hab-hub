from django.contrib import admin

from .models import TargetSpecies, DataLayer, Metric, MapBookmark

# Register models here.


class DataLayerAdmin(admin.ModelAdmin):
    pass


class MetricAdmin(admin.ModelAdmin):
    pass


class TargetSpeciesAdmin(admin.ModelAdmin):
    readonly_fields = ("color_gradient",)
    list_display = ("display_name", "species_id", "species_type", "species_subtype")
    list_filter = ("species_type", "species_subtype", "species_environment")


class MapBookmarkAdmin(admin.ModelAdmin):
    pass


admin.site.register(TargetSpecies, TargetSpeciesAdmin)
admin.site.register(DataLayer, DataLayerAdmin)
admin.site.register(Metric, MetricAdmin)
admin.site.register(MapBookmark, MapBookmarkAdmin)
