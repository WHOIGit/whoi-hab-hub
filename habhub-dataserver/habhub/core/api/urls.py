from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import (
    DataDensityAPIView,
    TargetSpeciesViewSet,
    DataLayerViewSet,
    MapBookmarkViewSet,
)
from habhub.stations.api.views import StationViewSet
from habhub.ifcb_datasets.api.views import (
    DatasetViewSet,
    BinViewSet,
    BinSpatialGridViewSet,
    AutoclassScoreViewSet,
    BinMetadataViewSet,
    DatasetBasicViewSet,
)
from habhub.closures.api.views import (
    ShellfishAreaViewSet,
    ShellfishAreaAllDataViewSet,
)

from habhub.monitoring_systems.api.views import (
    MonitoringSystemViewSet,
    ForecastingSystemViewSet,
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"core/data-density", DataDensityAPIView, "data-density")
router.register(r"core/target-species", TargetSpeciesViewSet, "target-species")
router.register(r"core/data-layers", DataLayerViewSet, "data-layers")
router.register(r"core/map-bookmarks", MapBookmarkViewSet, "map-bookmarks")
router.register(r"ifcb-datasets", DatasetViewSet, "ifcb-datasets")
router.register(r"ifcb-spatial-grid", BinSpatialGridViewSet, "ifcb-spatial-grid")
router.register(r"ifcb-bins", BinViewSet, "ifcb-bins")
router.register(r"closures", ShellfishAreaViewSet, "closures")
router.register(r"area-closures", ShellfishAreaAllDataViewSet, "area-closures")
router.register(r"stations", StationViewSet, "stations")
router.register(r"scores", AutoclassScoreViewSet, "scores")
router.register(r"bins", BinMetadataViewSet, "bins")
router.register(r"datasets", DatasetBasicViewSet, "datasets")
router.register(r"monitoring-systems", MonitoringSystemViewSet, "monitoring-systems")
router.register(r"forecasting-systems", ForecastingSystemViewSet, "forecasting-systems")

app_name = "api_v1"
urlpatterns = [
    path("", include(router.urls)),
]
