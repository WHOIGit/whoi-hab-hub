from django.contrib import admin

from .models import TargetSpecies, DataLayer

# Register models here.


class DataLayerAdmin(admin.ModelAdmin):
    readonly_fields = ('layer_id',)


admin.site.register(TargetSpecies)
admin.site.register(DataLayer, DataLayerAdmin)
