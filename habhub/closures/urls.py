from django.urls import path
from djgeojson.views import GeoJSONLayerView

from . import views

app_name = 'closures'
urlpatterns = [
    path('', views.ClosureHomeView.as_view(), name='closures_home'),
    path('status/', views.ClosureHomeView2.as_view(), name='closures_home2'),
    #path('status3/', views.ClosureHomeView3.as_view(), name='closures_home3'),
    #path('ajax/load-data/', views.ClosureAreaAjaxView.as_view(), name='ajax_closures_data'),
    #path('ajax/load-geojson-state/<state_code>/', views.ClosureAreaAjaxGeoLayerByStateView.as_view(), name='ajax_load_closure_areas_state'),
    #path('ajax/load-geojson-status/<current_status>/', views.ClosureAreaAjaxGeoLayerByStatusView.as_view(), name='ajax_load_closure_areas_status'),
    #path('ajax/load-geojson-detail/<int:pk>/', view=views.ClosureAreaAjaxGeoLayerSingleView.as_view(), name='ajax_load_closure_area'),
]
