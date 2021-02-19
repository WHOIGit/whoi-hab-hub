from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import DatasetViewSet

# Create a router and register our viewsets with it.
router = SimpleRouter()
router.register(r'ifcb-datasets', DatasetViewSet, 'ifcb-datasets' )

urlpatterns = [
    path('', include(router.urls) ),
]
