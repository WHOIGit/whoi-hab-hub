from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import DataDensityAPIView, TargetSpeciesViewSet, DataLayerViewSet

# Create a router and register our viewsets with it.
router = SimpleRouter()
router.register(r'core/data-density', DataDensityAPIView, 'data-density')
router.register(r'core/target-species', TargetSpeciesViewSet, 'target-species')
router.register(r'core/data-layers', DataLayerViewSet, 'data-layers')

urlpatterns = [
    path('', include(router.urls)),
]
