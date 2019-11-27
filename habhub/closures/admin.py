from django.contrib.gis import admin
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point, LineString, MultiLineString, Polygon, MultiPolygon
from django.db.models import FloatField, ExpressionWrapper, Func

from leaflet.admin import LeafletGeoAdmin, LeafletGeoAdminMixin
from leaflet.forms.widgets import LeafletWidget

from django_summernote.widgets import SummernoteWidget
from django_summernote.admin import SummernoteModelAdmin, SummernoteInlineModelAdmin

import geopy
import geopy.distance

from .models import *
from .forms import LandmarkForm

# Register your models here.

class LandmarkAdmin(LeafletGeoAdmin):
    form = LandmarkForm
    list_display = ('name', 'state', 'geom')
    list_editable = ('geom', )


class ShellfishAreaAdmin(LeafletGeoAdmin):
    ordering = ['state', 'name']
    search_fields = ['name']
    list_display = ('name', 'state')
    list_filter = ('state',)


class ClosureNoticeAdmin(admin.ModelAdmin):
    #autocomplete_fields = ['closure_areas']
    list_display = ('title', 'notice_date', 'notice_action', 'get_state', 'get_shellfish_areas')
    exclude = ('custom_borders', 'custom_geom', 'border_east', 'border_west')
    list_filter = ('shellfish_areas__state', 'notice_action',)
    filter_horizontal = ('shellfish_areas', )

    formfield_overrides = {
        models.TextField: {'widget': SummernoteWidget},
    }

    def get_queryset(self, request):
        return ClosureNotice.objects.exclude(shellfish_areas__state='ME')


class ExceptionAreaAdminInline(admin.StackedInline):
    model = ExceptionArea

    extra = 1

    formfield_overrides = {
        models.TextField: {'widget': SummernoteWidget},
        #models.MultiPolygonField: {'widget': LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS)}
    }


class ClosureNoticeMaineAdmin(LeafletGeoAdmin):
    list_display = ('title', 'notice_date', 'notice_action', 'get_state', 'get_shellfish_areas', 'custom_geom')
    list_editable = ('custom_geom', )
    exclude = ('custom_geom', 'custom_borders')
    list_filter = ('notice_action',)
    filter_horizontal = ('shellfish_areas', 'border_east', 'border_west')
    #autocomplete_fields = ['closure_areas']
    # Set Leaflet map settings to Maine coast
    settings_overrides = {
       'DEFAULT_CENTER': (43.786, -69.159),
       'DEFAULT_ZOOM': 8,
    }

    formfield_overrides = {
        models.TextField: {'widget': SummernoteWidget},
    }

    inlines = (ExceptionAreaAdminInline, )

    def get_queryset(self, request):
        return ClosureNotice.objects.filter(shellfish_areas__state='ME')

    # Override save method to create the custom geometry if custom_borders exist
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.border_east.exists():
            try:
                base_shape = BaseAreaShape.objects.get(name="Maine Coastline")
            except BaseAreaShape.DoesNotExist:
                base_shape = None

            if base_shape:
                base_polygon = base_shape.geom
                # loop through border points to make line
                #border_east = obj.border_east.all()
                border_east_coords = []
                border_east = obj.border_east.all().annotate(lat=ExpressionWrapper(Func('geom', function='ST_Y'), output_field=FloatField())).order_by('-lat')

                for i, point in enumerate(border_east):
                    # most northern point
                    if i == 0:
                        d = geopy.distance.distance(kilometers = 100)
                        north_point = d.destination(point=(point.geom.y, point.geom.x), bearing=315)
                        print(point.geom.y)
                        print(north_point.latitude)
                        print(north_point.longitude)
                        # convert geopy point to GEOS
                        north_point_geos = Point(north_point.longitude, north_point.latitude)
                        border_east_coords.append(north_point_geos.coords)

                    # add the selected point to line
                    border_east_coords.append(point.geom.coords)

                    # most southern point
                    if i == len(border_east) - 1:
                        d = geopy.distance.distance(kilometers = 100)
                        south_point = d.destination(point=(point.geom.y, point.geom.x), bearing=135)
                        print(south_point.latitude)
                        print(south_point.longitude)
                        # convert geopy point to GEOS
                        south_point_geos = Point(south_point.longitude, south_point.latitude)
                        border_east_coords.append(south_point_geos.coords)

                print(border_east_coords)

        """
        if obj.custom_borders:
            try:
                base_shape = BaseAreaShape.objects.get(name="Maine Coastline")
            except BaseAreaShape.DoesNotExist:
                base_shape = None

            if base_shape:
                base_polygon = base_shape.geom
                # create polygon from custom border lines
                polygon_mask = obj.custom_borders.convex_hull
                # create new geometry from base map with the mask
                new_shape = base_polygon.intersection(polygon_mask)

                if isinstance(new_shape, Polygon):
                    new_shape = MultiPolygon(new_shape)

                obj.custom_geom = new_shape
                obj.save()
        """

admin.site.register(ShellfishArea, ShellfishAreaAdmin)

admin.site.register(ClosureNotice, ClosureNoticeAdmin)

admin.site.register(ClosureNoticeMaine, ClosureNoticeMaineAdmin)

admin.site.register(Landmark, LandmarkAdmin)

admin.site.register(Species)

admin.site.register(CausativeOrganism)

admin.site.register(ExceptionArea, LeafletGeoAdmin)

admin.site.register(BaseAreaShape, LeafletGeoAdmin)
