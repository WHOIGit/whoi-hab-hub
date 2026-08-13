import datetime
from urllib.parse import unquote
from rest_framework import viewsets
from drf_multiple_model.viewsets import ObjectMultipleModelAPIViewSet
from django_filters import rest_framework as filters
from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncMonth

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

        active_layers = DataLayer.objects.filter(is_active=True)
        # filter the layers to use if there's a data_layer url parameter
        if data_layers:
            active_layers = active_layers.filter(layer_id__in=data_layers)
        querylist = []

        for layer in active_layers:
            if layer.layer_id == CELL_CONCENTRATION_LAYER:
                querylist.append(
                    {
                        "queryset": self._get_density_rows(
                            bins_qs.filter(cell_concentration_data__isnull=False),
                            "sample_time",
                        ),
                        "serializer_class": BinSerializer,
                        "label": "IFCB Cell Concentrations",
                    }
                )
            elif layer.layer_id == STATIONS_LAYER:
                querylist.append(
                    {
                        "queryset": self._get_density_rows(
                            datapoints_qs, "measurement_date"
                        ),
                        "serializer_class": DatapointSerializer,
                        "label": "Shellfish Station Toxicity",
                    }
                )
            elif layer.layer_id == CLOSURES_LAYER:
                querylist.append(
                    {
                        "queryset": self._get_density_rows(
                            closures_qs.filter(notice_action="Closed"),
                            "effective_date",
                        ),
                        "serializer_class": ClosureNoticeSerializer,
                        "label": "Shellfish Closures",
                    }
                )

        return querylist

    @staticmethod
    def _get_density_rows(queryset, date_field):
        """Group by month and count, then compute the max/density percentage
        in Python over the (small) grouped result instead of re-running the
        month/count aggregation a second time via a max subquery."""
        rows = list(
            queryset.annotate(timestamp=TruncMonth(date_field))
            .values("timestamp")
            .annotate(data_count=Count("id"))
            .order_by("timestamp")
        )
        if rows:
            max_count = max(row["data_count"] for row in rows)
            for row in rows:
                row["density_percentage"] = row["data_count"] / max_count
        return rows
