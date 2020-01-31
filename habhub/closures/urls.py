from django.urls import path
from djgeojson.views import GeoJSONLayerView

from . import views

app_name = 'closures'
urlpatterns = [
    path('', views.ClosureHomeView.as_view(), name='closures_home'),
    path('map-status/', views.ClosureMapShapeView.as_view(), name='closures_map_shapes'),
    path('map-cluster/', views.ClosureMapClusterView.as_view(), name='closures_map_cluster'),
    path('status/', views.ClosureHomeView2.as_view(), name='closures_home2'),
    path('status3/', views.ClosureHomeView3.as_view(), name='closures_home3'),
    # AJAX paths
    path('maps/ajax/load-all-closures/', views.ClosureNoticeAjaxGetAllView.as_view(), name='ajax_load_closures_all'),
    path('maps/ajax/load-closures-state/<state_code>/', views.ClosureNoticeAjaxGetLayerByStateView.as_view(), name='ajax_load_closures_by_state'),
    path('maps/ajax/load-all-closures-points/', views.ClosureNoticeAjaxGetAllPointsView.as_view(), name='ajax_load_closures_all_points'),
    path('maps/ajax/load-closures-state-points/<state_code>/', views.ClosureNoticeAjaxGetLayerByStatePointsView.as_view(), name='ajax_load_closures_by_state_points'),
    path('ajax/load-data/', views.ClosureAreaAjaxView.as_view(), name='ajax_closures_data'),
    path('ajax/load-geojson-state/<state_code>/', views.ClosureAreaAjaxGeoLayerByStateView.as_view(), name='ajax_load_closure_areas_state'),
    path('ajax/load-geojson-status/<current_status>/', views.ClosureAreaAjaxGeoLayerByStatusView.as_view(), name='ajax_load_closure_areas_status'),
    path('ajax/load-geojson-detail/<int:pk>/', view=views.ClosureAreaAjaxGeoLayerSingleView.as_view(), name='ajax_load_closure_area'),
]
