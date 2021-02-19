from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import StationViewSet

# Create a router and register our viewsets with it.
router = SimpleRouter()
router.register(r'stations', StationViewSet, 'stations' )

urlpatterns = [
    path('', include(router.urls) ),
]
