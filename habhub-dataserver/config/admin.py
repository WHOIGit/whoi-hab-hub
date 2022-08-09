from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path

from habhub.stations.views import (
    DatapointCsvUploadView,
    DatapointCsvUploadSuccessView,
    StationCsvUploadView,
    StationCsvUploadSuccessView,
)


class HabHubAdminSite(admin.AdminSite):
    index_template = "admin/custom_index.html"

    def get_urls(
        self,
    ):
        return [
            path(
                "upload_stations/",
                StationCsvUploadView.as_view(),
                name="upload_stations",
            ),
            path(
                "upload_stations_success/",
                StationCsvUploadSuccessView.as_view(),
                name="upload_stations_success",
            ),
            path(
                "upload_station_data/",
                DatapointCsvUploadView.as_view(),
                name="upload_station_data",
            ),
            path(
                "upload_station_data_success/",
                DatapointCsvUploadSuccessView.as_view(),
                name="upload_station_data_success",
            ),
        ] + super().get_urls()
