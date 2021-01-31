from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import DataDensityAPIView

# Create a router and register our viewsets with it.
router = SimpleRouter()
router.register(r'data-density', DataDensityAPIView, 'data-density' )

urlpatterns = [
    path('', include(router.urls) ),
]
