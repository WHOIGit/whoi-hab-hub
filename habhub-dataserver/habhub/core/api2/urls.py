from django.urls import path, include
from rest_framework.routers import DefaultRouter
from habhub.ifcb_datasets.api2.views import (
    ScoresIndexViewSet,
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"os-scores", ScoresIndexViewSet, "os-scores")

app_name = "api_v2"
urlpatterns = [
    path("", include(router.urls)),
]
