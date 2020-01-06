from django.urls import path

from . import views

app_name = 'monitoring_systems'
urlpatterns = [
    path('maps/us-monitoring-systems', views.MonitoringSystemMapUS.as_view(), name='monitoring_systems_map_us'),
]
