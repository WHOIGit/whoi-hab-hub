from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import DataDensityAPIView, TargetSpeciesViewSet, DataLayerViewSet
from habhub.stations.api.views import StationViewSet
from habhub.ifcb_datasets.api.views import DatasetViewSet, SpatialDatasetViewSet
from habhub.closures.api.views import ShellfishAreaViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'core/data-density', DataDensityAPIView, 'data-density')
router.register(r'core/target-species', TargetSpeciesViewSet, 'target-species')
router.register(r'core/data-layers', DataLayerViewSet, 'data-layers')
router.register(r'ifcb-datasets', DatasetViewSet, 'ifcb-datasets')
router.register(r'ifcb-datasets-spatial', SpatialDatasetViewSet, 'ifcb-datasets-spatial')
router.register(r'closures', ShellfishAreaViewSet, 'closures')
router.register(r'stations', StationViewSet, 'stations')

app_name = 'api_v1'
urlpatterns = [
    path('', include(router.urls)),
]
