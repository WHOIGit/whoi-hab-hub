from django.urls import path

from . import views

app_name = 'ifcb_cruises'
urlpatterns = [
    path('ajax/load-ifcb-data/', views.load_ifcb_cruise_data, name='ajax_load_ifcb_data'),
]
