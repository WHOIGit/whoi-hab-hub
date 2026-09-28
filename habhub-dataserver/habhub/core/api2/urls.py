from django.urls import path, include
from rest_framework.routers import DefaultRouter
from habhub.ifcb_datasets.api2.views import (
    SpeciesScoresIndexViewSet,
    IfcbFixedMetricsViewSet,
    IfcbSpatialGridViewSet,
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(
    r"ifcb-species-scores", SpeciesScoresIndexViewSet, "ifcb-species-scores"
)
router.register(r"ifcb-fixed-metrics", IfcbFixedMetricsViewSet, "ifcb-fixed-metrics")
router.register(r"ifcb-spatial-grid", IfcbSpatialGridViewSet, "ifcb-spatial-grid")

app_name = "api_v2"
urlpatterns = [
    path("", include(router.urls)),
]
