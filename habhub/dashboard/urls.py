from django.urls import path

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('map-main/', views.MapMainView.as_view(), name='map_main_home'),
]
