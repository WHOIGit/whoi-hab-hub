from django.db import models
from django.db.models import Subquery, OuterRef, Avg
from django.apps import apps

class StationQuerySet(models.QuerySet):

    def add_station_max(self, start_date=None, end_date=None):
        Datapoint = apps.get_model(app_label='stations', model_name='Datapoint')
        # set up the Subquery query with conditional date filter
        datapoint_query = Datapoint.objects.filter(station=OuterRef('id'))

        if start_date and end_date:
            datapoint_query = datapoint_query.filter(measurement_date__range=[start_date, end_date])

        # now get the Max value
        datapoint_query = (
            datapoint_query.order_by('-measurement')
                           .values('measurement')[:1] # Only have 1 row & 1 value
        )

        return self.annotate(
            station_max=Subquery(
               datapoint_query,
               output_field=models.DecimalField()
            )
        )

    def add_station_mean(self, start_date=None, end_date=None):
        Datapoint = apps.get_model(app_label='stations', model_name='Datapoint')
        # set up the base Subquery query with conditional date filter
        datapoint_query = Datapoint.objects.filter(station=OuterRef('id'))

        if start_date and end_date:
            datapoint_query = datapoint_query.filter(measurement_date__range=[start_date, end_date])

        # now get the Avg value for this set of Datapoints
        datapoint_query = (
            datapoint_query.values('station_id') # group cities by state
                           .order_by() # reset ordering
                           .annotate(station_mean=Avg('measurement'))
                           .values('station_mean')[:1] # Only have 1 row & 1 value allowed
        )

        return self.annotate(
            station_mean=Subquery(
               datapoint_query,
               output_field=models.DecimalField()
            )
        )
