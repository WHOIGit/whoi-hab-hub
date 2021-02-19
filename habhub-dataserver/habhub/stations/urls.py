from django.urls import path

from . import views

app_name = 'stations'
urlpatterns = [
    path('map-main/', views.StationMapMainView.as_view(), name='stations_map_main'),
    # AJAX paths
    path('maps/ajax/load-all-stations/', views.StationAjaxGetAllView.as_view(), name='ajax_load_stations_all'),
    path('maps/ajax/load-station-chart/<int:station_id>/', views.StationAjaxGetChartView.as_view(), name='ajax_load_station_chart'),
    # admin paths for data upload
    path('datapoints-upload/', views.DatapointCsvUploadView.as_view(), name='datapoints_upload_form'),
    path('datapoints-upload/success/', views.DatapointCsvUploadSuccessView.as_view(), name='datapoints_import_upload_success'),
]
