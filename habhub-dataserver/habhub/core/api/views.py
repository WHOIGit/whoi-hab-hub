import datetime
from urllib.parse import unquote
from rest_framework import viewsets
from drf_multiple_model.viewsets import ObjectMultipleModelAPIViewSet
from django_filters import rest_framework as filters
from django.db import models
from django.db.models import Count, Max, F, ExpressionWrapper, FloatField, Subquery
from django.db.models.functions import TruncMonth, Cast

from ..models import TargetSpecies, DataLayer, MapBookmark
from habhub.core.constants import (
    CELL_CONCENTRATION_LAYER,
    STATIONS_LAYER,
    CLOSURES_LAYER,
)
from habhub.stations.models import Datapoint
from habhub.ifcb_datasets.models import Bin
from habhub.closures.models import ClosureNotice
from .serializers import (
    DatapointSerializer,
    BinSerializer,
    ClosureNoticeSerializer,
    TargetSpeciesSerializer,
    DataLayerSerializer,
    MapBookmarkSerializer,
)


class TargetSpeciesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TargetSpeciesSerializer
    queryset = TargetSpecies.objects.all()


class DataLayerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DataLayerSerializer

    def get_queryset(self):
        queryset = DataLayer.objects.filter(is_active=True)
        return queryset


class MapBookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = MapBookmarkSerializer
    queryset = MapBookmark.objects.all()


class DataDensityAPIView(ObjectMultipleModelAPIViewSet):
    def get_querylist(self):
        print("REQUEST", self.request.query_params)
        data_layers = self.request.query_params.get("data_layers", None)
        limit_start_date = self.request.query_params.get("limit_start_date", None)

        if data_layers:
            data_layers = data_layers.split(",")

        if limit_start_date:
            # if limit_start_date param exists, run initial date filter on all data layers
            start_date_obj = datetime.datetime.strptime(
                limit_start_date, "%Y-%m-%d"
            ).date()

            datapoints_qs = Datapoint.objects.filter(
                measurement_date__gte=start_date_obj
            )
            bins_qs = Bin.objects.filter(sample_time__gte=start_date_obj)
            closures_qs = ClosureNotice.objects.filter(
                effective_date__gte=start_date_obj
            )
        else:
            datapoints_qs = Datapoint.objects.all()
            bins_qs = Bin.objects.all()
            closures_qs = ClosureNotice.objects.all()

        # use a separate subquery to get the max count value
        datapoint_max = (
            datapoints_qs.annotate(timestamp=TruncMonth("measurement_date"))
            .values("timestamp")
            .annotate(data_count=Count("id"))
            .order_by("-data_count")
            .values("data_count")[:1]
        )

        datapoint_query = (
            datapoints_qs
            # Truncate to Month and add to values
            .annotate(timestamp=TruncMonth("measurement_date"))
            .values("timestamp")  # Group By Month
            .annotate(data_count=Count("id"))  # Select the count of the grouping
            # Bring in the max value from a subquery
            .annotate(datapoint_max=Subquery(datapoint_max.values("data_count")[:1]))
            # calculate density percentage. Cast one of the integers to a Floatfield to make division return a float.
            .annotate(
                density_percentage=ExpressionWrapper(
                    Cast("data_count", FloatField()) / F("datapoint_max"),
                    output_field=FloatField(),
                )
            )
            .order_by("timestamp")
        )

        # use a separate subquery to get the max count value
        bin_max = (
            bins_qs.filter(cell_concentration_data__isnull=False)
            .annotate(timestamp=TruncMonth("sample_time"))
            .values("timestamp")
            .annotate(data_count=Count("id"))
            .order_by("-data_count")
            .values("data_count")[:1]
        )

        bin_query = (
            bins_qs.filter(cell_concentration_data__isnull=False)
            # Truncate to Month and add to values
            .annotate(timestamp=TruncMonth("sample_time"))
            .values("timestamp")  # Group By Month
            .annotate(data_count=Count("id"))  # Select the count of the grouping
            .annotate(
                bin_max=Subquery(bin_max.values("data_count")[:1])
            )  # Bring in the max value from a subquery
            # calculate density percentage. Cast one of the integers to a Floatfield to make division return a float.
            .annotate(
                density_percentage=ExpressionWrapper(
                    Cast("data_count", FloatField()) / F("bin_max"),
                    output_field=FloatField(),
                )
            )
            .order_by("timestamp")
        )

        # use a separate subquery to get the max count value
        closure_max = (
            closures_qs.filter(notice_action="Closed")
            .annotate(timestamp=TruncMonth("effective_date"))
            .values("timestamp")
            .annotate(data_count=Count("id"))
            .order_by("-data_count")
            .values("data_count")[:1]
        )

        closure_query = (
            closures_qs.filter(notice_action="Closed")
            .annotate(
                timestamp=TruncMonth("effective_date")
            )  # Truncate to Month and add to values
            .values("timestamp")  # Group By Month
            .annotate(data_count=Count("id"))  # Select the count of the grouping
            .annotate(
                closure_max=Subquery(closure_max.values("data_count")[:1])
            )  # Bring in the max value from a subquery
            # calculate density percentage. Cast one of the integers to a Floatfield to make division return a float.
            .annotate(
                density_percentage=ExpressionWrapper(
                    Cast("data_count", FloatField()) / F("closure_max"),
                    output_field=FloatField(),
                )
            )
            .order_by("timestamp")
        )

        active_layers = DataLayer.objects.filter(is_active=True)
        # filter the layers to use if there's a data_layer url parameter
        if data_layers:
            active_layers = active_layers.filter(layer_id__in=data_layers)
        querylist = []

        for layer in active_layers:
            if layer.layer_id == CELL_CONCENTRATION_LAYER:
                querylist.append(
                    {
                        "queryset": bin_query,
                        "serializer_class": BinSerializer,
                        "label": "IFCB Cell Concentrations",
                    }
                )
            elif layer.layer_id == STATIONS_LAYER:
                querylist.append(
                    {
                        "queryset": datapoint_query,
                        "serializer_class": DatapointSerializer,
                        "label": "Shellfish Station Toxicity",
                    }
                )
            elif layer.layer_id == CLOSURES_LAYER:
                querylist.append(
                    {
                        "queryset": closure_query,
                        "serializer_class": ClosureNoticeSerializer,
                        "label": "Shellfish Closures",
                    }
                )

        return querylist
