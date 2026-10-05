import copy
from decimal import Decimal

import pytest
from django.contrib.gis.geos import Point
from django.core.cache import cache
from rest_framework.test import APIClient

from habhub.core.models import DataLayer, Metric, TargetSpecies
from habhub.ifcb_datasets.api2 import views as api2_views
from habhub.ifcb_datasets.models import Dataset


class FakeOpenSearch:
    """
    Stand in for the Opensearch client used by the v2 views. Records every search
    and returns the response set for the index, or the result of calling it with
    the search body.
    """

    def __init__(self):
        self.responses = {}
        self.searches = []

    def search(self, body=None, index=None, **kwargs):
        # copy the body, views update the same query dict to get the next page
        self.searches.append({"index": index, "body": copy.deepcopy(body), "kwargs": kwargs})
        response = self.responses.get(index, {"hits": {"hits": []}})
        return response(body) if callable(response) else response

    def searches_for(self, index):
        return [search for search in self.searches if search["index"] == index]


@pytest.fixture(autouse=True)
def clear_cache():
    # the API views cache their responses
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def fake_opensearch(monkeypatch):
    client = FakeOpenSearch()
    monkeypatch.setattr(api2_views, "connect_opensearch", lambda: client)
    return client


@pytest.fixture
def target_species(db):
    # the migrations add the default TargetSpecies, keep two with different
    # thresholds. update() skips TargetSpecies.save(), which starts data tasks
    # when a threshold changes
    TargetSpecies.objects.exclude(species_id__in=["Karenia", "Pseudo-nitzschia"]).delete()
    TargetSpecies.objects.filter(species_id="Karenia").update(
        autoclass_threshold=Decimal("0.95")
    )
    TargetSpecies.objects.filter(species_id="Pseudo-nitzschia").update(
        autoclass_threshold=Decimal("0.50")
    )
    return list(TargetSpecies.objects.order_by("species_id"))


@pytest.fixture
def ifcb_metrics(db):
    # the migrations add the default Metrics and DataLayers
    return list(
        Metric.objects.filter(
            data_layers__belongs_to_app=DataLayer.IFCB_DATASETS
        ).distinct()
    )


@pytest.fixture
def dataset(db):
    return Dataset.objects.create(
        name="Harpswell",
        location="Maine",
        dashboard_id_name="harpswell",
        dashboard_public_url="https://ifcb.example.org",
        geom=Point(-70.0, 44.0, srid=4326),
    )
