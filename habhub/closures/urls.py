from django.urls import path
from djgeojson.views import GeoJSONLayerView

from .models import ClosureArea
from . import views

app_name = 'closures'
urlpatterns = [
    path('', views.ClosureHomeView.as_view(), name='closures_home'),
    path('ajax/load-geojson/', GeoJSONLayerView.as_view(model=ClosureArea, properties=('name',)), name='load_closure_areas')
]
