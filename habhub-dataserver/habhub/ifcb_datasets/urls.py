from django.urls import path

from . import views

app_name = "ifcb-datasets"
urlpatterns = [
    # AJAX paths
    path(
        "maps/ajax/get-bin-images-species/",
        views.BinAjaxGetImagesBySpecies.as_view(),
        name="ajax_get_bin_images_by_species",
    ),
]
