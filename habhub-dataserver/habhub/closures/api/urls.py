from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import ShellfishAreaViewSet

# Create a router and register our viewsets with it.
router = SimpleRouter()
#router.register(r'closures', ClosureDataEventViewSet, 'closures' )
router.register(r'closures', ShellfishAreaViewSet, 'closures' )

urlpatterns = [
    path('', include(router.urls) ),
]
