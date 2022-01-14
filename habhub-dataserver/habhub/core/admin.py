from django.contrib import admin

from .models import TargetSpecies, DataLayer, Metric, MapBookmark

# Register models here.


class DataLayerAdmin(admin.ModelAdmin):
    pass


class MetricAdmin(admin.ModelAdmin):
    pass


class TargetSpeciesAdmin(admin.ModelAdmin):
    readonly_fields = ("color_gradient",)


class MapBookmarkAdmin(admin.ModelAdmin):
    pass


admin.site.register(TargetSpecies, TargetSpeciesAdmin)
admin.site.register(DataLayer, DataLayerAdmin)
admin.site.register(Metric, MetricAdmin)
admin.site.register(MapBookmark, MapBookmarkAdmin)
