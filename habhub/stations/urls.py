from django.urls import path

from . import views

app_name = 'stations'
urlpatterns = [
    path('map-main/', views.StationMapMainView.as_view(), name='stations_map_main'),
    # AJAX paths
    path('maps/ajax/load-all-stations/', views.StationAjaxGetAllView.as_view(), name='ajax_load_stations_all'),
]
