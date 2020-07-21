from django.urls import path

from . import views

app_name = 'ifcb_datasets'
urlpatterns = [
    path('map-main/', views.IFCBMapMainView.as_view(), name='ifcb_map_main'),
    # AJAX paths
    path('maps/ajax/load-all-stations/', views.DatasetAjaxGetAllView.as_view(), name='ajax_load_datasets_all'),
    #path('maps/ajax/load-station-chart/<int:station_id>/', views.DatasetAjaxGetChartView.as_view(), name='ajax_load_dataset_chart'),
]
