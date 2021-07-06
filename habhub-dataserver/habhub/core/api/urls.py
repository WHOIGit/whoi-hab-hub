from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter
from .views import DataDensityAPIView, TargetSpeciesViewSet, DataLayerViewSet
from habhub.stations.api.views import StationViewSet
from habhub.ifcb_datasets.api.views import DatasetViewSet
from habhub.closures.api.views import ShellfishAreaViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'core/data-density', DataDensityAPIView, 'data-density')
router.register(r'core/target-species', TargetSpeciesViewSet, 'target-species')
router.register(r'core/data-layers', DataLayerViewSet, 'data-layers')
router.register(r'ifcb-datasets', DatasetViewSet, 'ifcb-datasets')
router.register(r'closures', ShellfishAreaViewSet, 'closures')
router.register(r'stations', StationViewSet, 'stations')

app_name = 'api_v1'
urlpatterns = [
    path('', include(router.urls)),
    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),  # override sjwt stock token
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
