from django.urls import path

from . import views

app_name = 'ifcb-datasets'
urlpatterns = [
    path('map-main/', views.IFCBMapMainView.as_view(), name='ifcb_map_main'),
    # AJAX paths
    path('maps/ajax/load-all-datasets/', views.DatasetAjaxGetAllView.as_view(), name='ajax_load_datasets_all'),
    path('maps/ajax/get-sidebar/', views.DatasetAjaxGetMapSidebar.as_view(), name='ajax_get_dataset_map_sidebar'),
    path('maps/ajax/get-sidebar/<int:pk>/', views.DatasetAjaxGetMapSidebar.as_view(), name='ajax_get_dataset_map_sidebar'),
    path('maps/ajax/get-bin-images-species/', views.BinAjaxGetImagesBySpecies.as_view(), name='ajax_get_bin_images_by_species'),
]
