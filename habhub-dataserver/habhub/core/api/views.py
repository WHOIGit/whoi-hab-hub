import datetime

from drf_multiple_model.viewsets import ObjectMultipleModelAPIViewSet
from django_filters import rest_framework as filters
from django.db import models
from django.db.models import Count, Max, F, ExpressionWrapper, FloatField, Subquery
from django.db.models.functions import TruncDay, TruncMonth, Cast

from habhub.stations.models import Datapoint
from habhub.ifcb_datasets.models import Bin
from habhub.closures.models import ClosureNotice
from .serializers import (
    DatapointSerializer, BinSerializer, ClosureNoticeSerializer
)


class DataDensityAPIView(ObjectMultipleModelAPIViewSet):
    # use a separate subquery to get the max count value
    datapoint_max = (
        Datapoint.objects
        .annotate(timestamp=TruncMonth('measurement_date'))
        .values('timestamp')
        .annotate(data_count=Count('id'))
        .order_by('-data_count')
        .values('data_count')[:1]
    )

    datapoint_query = (
        Datapoint.objects
        # Truncate to Month and add to values
        .annotate(timestamp=TruncMonth('measurement_date'))
        .values('timestamp')  # Group By Month
        .annotate(data_count=Count('id'))  # Select the count of the grouping
        .annotate(datapoint_max=Subquery(datapoint_max.values('data_count')[:1])) # Bring in the max value from a subquery
        # calculate density percentage. Cast one of the integers to a Floatfield to make division return a float.
        .annotate(density_percentage=ExpressionWrapper(
            Cast('data_count', FloatField()) / F('datapoint_max'), output_field=FloatField()
            ))
        .order_by('timestamp')
    )

    # use a separate subquery to get the max count value
    bin_max = (
        Bin.objects
        .annotate(timestamp=TruncMonth('sample_time'))
        .values('timestamp')
        .annotate(data_count=Count('id'))
        .order_by('-data_count')
        .values('data_count')[:1]
    )

    bin_query = (
        Bin.objects
        # Truncate to Month and add to values
        .annotate(timestamp=TruncMonth('sample_time'))
        .values('timestamp')  # Group By Month
        .annotate(data_count=Count('id'))  # Select the count of the grouping
        .annotate(bin_max=Subquery(bin_max.values('data_count')[:1])) # Bring in the max value from a subquery
        # calculate density percentage. Cast one of the integers to a Floatfield to make division return a float.
        .annotate(density_percentage=ExpressionWrapper(
            Cast('data_count', FloatField()) / F('bin_max'), output_field=FloatField()
            ))
        .order_by('timestamp')
    )

    # use a separate subquery to get the max count value
    closure_max = (
        ClosureNotice.objects.filter(notice_action="Closed")
        .annotate(timestamp=TruncMonth('effective_date'))
        .values('timestamp')
        .annotate(data_count=Count('id'))
        .order_by('-data_count')
        .values('data_count')[:1]
    )

    closure_query = (
        ClosureNotice.objects
        .filter(notice_action="Closed")
        .annotate(timestamp=TruncMonth('effective_date')) # Truncate to Month and add to values
        .values('timestamp')  # Group By Month
        .annotate(data_count=Count('id'))  # Select the count of the grouping
        .annotate(closure_max=Subquery(closure_max.values('data_count')[:1])) # Bring in the max value from a subquery
        # calculate density percentage. Cast one of the integers to a Floatfield to make division return a float.
        .annotate(density_percentage=ExpressionWrapper(
            Cast('data_count', FloatField()) / F('closure_max'), output_field=FloatField()
            ))
        .order_by('timestamp')
    )

    querylist = [
        {
            'queryset': closure_query,
            'serializer_class': ClosureNoticeSerializer,
            'label': 'Shellfish Closures',
        },
        {
            'queryset': bin_query,
            'serializer_class': BinSerializer,
            'label': 'IFCB Cell Concentrations',
        },
        {
            'queryset': datapoint_query,
            'serializer_class': DatapointSerializer,
            'label': 'Shellfish Station Toxicity',
        },
    ]
