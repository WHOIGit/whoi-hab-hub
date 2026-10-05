import datetime

import pytest
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from habhub.ifcb_datasets.api2.mixins import ScoresFiltersMixin
from habhub.ifcb_datasets.api2.views import (
    IfcbBinViewSet,
    IfcbSpatialGridViewSet,
    decode_geohash_center,
    encode_geohash,
    snap_to_grid,
)
from habhub.ifcb_datasets.opensearch import build_histogram_fields


class TestGeohash:
    def test_encode_matches_postgis(self):
        # PostGIS ST_GeoHash() values, the v1 spatial grid square IDs
        assert encode_geohash(44.0, -70.0) == "dry4r"
        assert encode_geohash(0.0, 0.0) == "s0000"
        assert encode_geohash(-90.0, -180.0) == "00000"

    def test_decode_center_snaps_back_to_grid_point(self):
        lat, lng = decode_geohash_center("dry4r")
        assert snap_to_grid(lng, 0.5) == -70.0
        assert snap_to_grid(lat, 0.5) == 44.0

    def test_decode_invalid(self):
        # "a", "i", "l" and "o" aren't geohash characters
        assert decode_geohash_center("abcde") is None


class TestSnapToGrid:
    def test_rounds_half_to_even(self):
        # same as PostGIS ST_SnapToGrid()
        assert snap_to_grid(0.25, 0.5) == 0.0
        assert snap_to_grid(0.75, 0.5) == 1.0
        assert snap_to_grid(-70.1, 0.5) == -70.0
        assert snap_to_grid(-69.8, 0.5) == -70.0


class TestHistogramFields:
    def test_encodes_bucket_and_count(self):
        species_scores = {"Karenia": {"modelA": [[42, 1], [99, 12]], "modelB": [[50, 3]]}}

        assert build_histogram_fields(species_scores) == {
            "Karenia": {"modelA": [42000001, 99000012], "modelB": [50000003]}
        }


def filters_for(view_class, params=None):
    # run ScoresFiltersMixin.handle_query_param_filters() for a request
    view = view_class()
    view.request = Request(APIRequestFactory().get("/", params or {}))
    return view.handle_query_param_filters()


def sample_time_range(query):
    return next(
        clause["range"]["sampleTime"]
        for clause in query["query"]["bool"]["must"]
        if "sampleTime" in clause.get("range", {})
    )


class TestScoresFilters:
    def test_date_params(self):
        query = filters_for(
            ScoresFiltersMixin, {"start_date": "2026-08-01", "end_date": "2026-08-31"}
        )
        assert sample_time_range(query) == {"gte": "2026-08-01", "lte": "2026-08-31"}

    @pytest.mark.parametrize(
        "view_class, days",
        [(ScoresFiltersMixin, 365), (IfcbSpatialGridViewSet, 365), (IfcbBinViewSet, 31)],
    )
    def test_default_date_range(self, view_class, days):
        # the bins list defaults to the past month, the other views to the past year
        start = datetime.datetime.fromisoformat(sample_time_range(filters_for(view_class))["gte"])
        assert abs((timezone.now() - start) - datetime.timedelta(days=days)) < datetime.timedelta(days=2)

    def test_dataset_species_and_bbox_filters(self):
        query = filters_for(
            ScoresFiltersMixin,
            {
                "dataset_id": "harpswell,mvco",
                "species": "Karenia",
                "bbox_sw": "-71,41",
                "bbox_ne": "-69,43",
            },
        )
        must = query["query"]["bool"]["must"]
        assert {"terms": {"datasetId": ["harpswell", "mvco"]}} in must
        assert {"terms": {"species": ["Karenia"]}} in must
        assert query["query"]["bool"]["filter"] == {
            "geo_bounding_box": {
                "point": {"bottom_left": [-71.0, 41.0], "top_right": [-69.0, 43.0]}
            }
        }
