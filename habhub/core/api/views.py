import datetime

from drf_multiple_model.viewsets import ObjectMultipleModelAPIViewSet
from django_filters import rest_framework as filters
from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncMonth

from habhub.stations.models import Datapoint
from habhub.ifcb_datasets.models import Bin
from habhub.closures.models import ClosureNotice
from .serializers import (
    DatapointSerializer, BinSerializer, ClosureNoticeSerializer
)


class DataDensityAPIView(ObjectMultipleModelAPIViewSet):
    datapoint_query =  (
        Datapoint.objects
            .annotate(timestamp=TruncDay('measurement_date')) # Truncate to Day and add to select list
            .values('timestamp') # Group By Day
            .annotate(count=Count('id')) # Select the count of the grouping
            .order_by('timestamp')
    )

    bin_query =  (
        Bin.objects
            .annotate(timestamp=TruncDay('sample_time')) # Truncate to Day and add to select list
            .values('timestamp') # Group By Day
            .annotate(count=Count('id')) # Select the count of the grouping
            .order_by('timestamp')
    )

    closure_query =  (
        ClosureNotice.objects
            .filter(notice_action="Closed")
            .annotate(timestamp=TruncMonth('effective_date')) # Truncate to Day and add to select list
            .values('timestamp') # Group By Day
            .annotate(count=Count('id')) # Select the count of the grouping
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
