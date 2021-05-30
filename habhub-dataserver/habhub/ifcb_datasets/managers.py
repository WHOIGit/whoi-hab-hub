from django.db import models
from django.db.models import Subquery, OuterRef
from django.contrib.gis.db.models import Extent
from django.apps import apps
from django.contrib.gis.geos import Point

class DatasetQuerySet(models.QuerySet):

    def add_bins_geo_extent(self, date_q_filters=None):
        Bin = apps.get_model(app_label='ifcb_datasets', model_name='Bin')
        zero_pt = Point(0, 0)
        # set up the Subquery query with conditional date filter
        bin_query = Bin.objects.filter(dataset=OuterRef('id'))

        if date_q_filters:
            bin_query = bin_query.filter(date_q_filters)

        bin_query = (
            bin_query.filter(geom__isnull=False)
            .filter(cell_concentration_data__isnull=False)
            .exclude(geom=zero_pt)
        )

        # now aggregate all filtered Bins to get Extent, but use annotate in subquery
        bin_query = (
            bin_query.values('dataset_id') # group by dataset
            .order_by() # reset ordering
            .annotate(bins_geo_extent=Extent('geom'))
            .values('bins_geo_extent')[:1]
        )

        return self.annotate(
            bins_geo_extent=Subquery(
               bin_query
            )
        )
