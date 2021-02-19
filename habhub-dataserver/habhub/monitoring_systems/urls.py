from django.urls import path

from . import views

app_name = 'monitoring_systems'
urlpatterns = [
    path('maps/us-monitoring-systems/', views.MonitoringSystemMapUS.as_view(), name='monitoring_systems_map_us'),
    # AJAX paths
    path('maps/ajax/load-all-systems/', views.MonitoringSystemAjaxGetAllView.as_view(), name='ajax_load_monitoring_systems_all'),
    path('maps/ajax/load-all-monitoring-systems/', views.MonitoringSystemAjaxGetMonitoringView.as_view(), name='ajax_load_monitoring_systems'),
    path('maps/ajax/load-all-forecasting-systems/', views.MonitoringSystemAjaxGetForecastingView.as_view(), name='ajax_load_forecasting_systems'),
]
