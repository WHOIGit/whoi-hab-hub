from django.contrib import admin

from .models import TargetSpecies, DataLayer

# Register models here.


class DataLayerAdmin(admin.ModelAdmin):
    readonly_fields = ('layer_id',)


class TargetSpeciesAdmin(admin.ModelAdmin):
    readonly_fields = ('color_gradient',)


admin.site.register(TargetSpecies, TargetSpeciesAdmin)
admin.site.register(DataLayer, DataLayerAdmin)
