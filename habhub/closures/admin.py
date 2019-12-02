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

    def get_queryset(self, request):
        if request.user.groups.filter(name = 'Closures - Massachusetts Only').exists():
            qs = ShellfishArea.objects.filter(state='MA')
        elif request.user.groups.filter(name = 'Closures - New Hampshire Only').exists():
            qs = ShellfishArea.objects.filter(state='NH')
        else:
            qs = ShellfishArea.objects.all()
        return qs

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'state':
            if request.user.groups.filter(name = 'Closures - Massachusetts Only').exists():
                kwargs['choices'] = (
                    ('MA', 'Massachusetts'),
                )
            elif request.user.groups.filter(name = 'Closures - Maine Only').exists():
                kwargs['choices'] = (
                    ('ME', 'Maine'),
                )
            elif request.user.groups.filter(name = 'Closures - New Hampshire Only').exists():
                kwargs['choices'] = (
                    ('NH', 'New Hampshire'),
                )
        return super().formfield_for_choice_field(db_field, request, **kwargs)


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
        if request.user.groups.filter(name = 'Closures - Massachusetts Only').exists():
            qs = ClosureNotice.objects.filter(shellfish_areas__state='MA').distinct()
        elif request.user.groups.filter(name = 'Closures - New Hampshire Only').exists():
            qs = ClosureNotice.objects.filter(shellfish_areas__state='NH').distinct()
        else:
            qs = ClosureNotice.objects.exclude(shellfish_areas__state='ME')
        return qs

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        state_filter = None

        if request.user.groups.filter(name = 'Closures - Massachusetts Only').exists():
            state_filter = 'MA'
        elif request.user.groups.filter(name = 'Closures - New Hampshire Only').exists():
            state_filter = 'NH'

        if db_field.name == 'shellfish_areas' and state_filter:
            kwargs["queryset"] = ShellfishArea.objects.filter(state=state_filter)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


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

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'shellfish_areas':
            kwargs["queryset"] = ShellfishArea.objects.filter(state='ME')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # Override save method to create the custom geometry if custom_borders exist
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.border_east.exists() or obj.border_west.exists():
            try:
                base_shape = BaseAreaShape.objects.get(name="Maine Coastline")
            except BaseAreaShape.DoesNotExist:
                base_shape = None

            if base_shape:
                base_polygon = base_shape.geom
                # Set the distance to go North/South from final points to set polygon mask
                distance_togo_north = geopy.distance.distance(kilometers = 5)
                distance_togo_south = geopy.distance.distance(kilometers = 100)
                # Create custom eastern border
                border_east_coords = []
                border_east = obj.border_east.all().annotate(lat=ExpressionWrapper(Func('geom', function='ST_Y'), output_field=FloatField())).order_by('-lat')

                for i, point in enumerate(border_east):
                    # most northern point
                    if i == 0:
                        # Create new Point that is 100km North of last point
                        north_point = distance_togo_north.destination(point=(point.geom.y, point.geom.x), bearing=0)
                        # convert geopy point to GEOS
                        north_point_geos = Point(north_point.longitude, north_point.latitude)
                        border_east_coords.append(north_point_geos.coords)

                    # add the selected point to line
                    border_east_coords.append(point.geom.coords)

                    # most southern point
                    if i == len(border_east) - 1:
                        # Create new Point that is 100km South of last point
                        south_point = distance_togo_south.destination(point=(point.geom.y, point.geom.x), bearing=180)
                        # convert geopy point to GEOS
                        south_point_geos = Point(south_point.longitude, south_point.latitude)
                        border_east_coords.append(south_point_geos.coords)

                # Create custom western border
                border_west_coords = []
                border_west = obj.border_west.all().annotate(lat=ExpressionWrapper(Func('geom', function='ST_Y'), output_field=FloatField())).order_by('-lat')

                for i, point in enumerate(border_west):
                    # most northern point
                    if i == 0:
                        north_point = distance_togo_north.destination(point=(point.geom.y, point.geom.x), bearing=0)
                        # convert geopy point to GEOS
                        north_point_geos = Point(north_point.longitude, north_point.latitude)
                        border_west_coords.append(north_point_geos.coords)

                    # add the selected point to line
                    border_west_coords.append(point.geom.coords)

                    # most southern point
                    if i == len(border_west) - 1:
                        south_point = distance_togo_south.destination(point=(point.geom.y, point.geom.x), bearing=180)
                        # convert geopy point to GEOS
                        south_point_geos = Point(south_point.longitude, south_point.latitude)
                        border_west_coords.append(south_point_geos.coords)

                # create linestrings from the lists of points
                border_east_linestring = LineString([coords for coords in border_east_coords])
                border_west_linestring = LineString([coords for coords in border_west_coords])
                multi_line = MultiLineString(border_east_linestring, border_west_linestring)

                # create polygon from custom border lines
                polygon_mask = multi_line.convex_hull

                # create new geometry from base map with the mask
                new_shape = base_polygon.intersection(polygon_mask)

                if isinstance(new_shape, Polygon):
                    new_shape = MultiPolygon(new_shape)

                obj.custom_geom = new_shape
                obj.save()


admin.site.register(ShellfishArea, ShellfishAreaAdmin)

admin.site.register(ClosureNotice, ClosureNoticeAdmin)

admin.site.register(ClosureNoticeMaine, ClosureNoticeMaineAdmin)

admin.site.register(Landmark, LandmarkAdmin)

admin.site.register(Species)

admin.site.register(CausativeOrganism)

admin.site.register(ExceptionArea, LeafletGeoAdmin)

admin.site.register(BaseAreaShape, LeafletGeoAdmin)
