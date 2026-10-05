import datetime

import pytest
from django.contrib.gis.geos import Point

from habhub.ifcb_datasets.models import Bin

pytestmark = pytest.mark.django_db

DATE_PARAMS = {"start_date": "2026-08-01", "end_date": "2026-08-31"}


def concentration_data(karenia, pseudo_nitzschia, pid):
    # Bin.cell_concentration_data for the test target species
    return [
        {
            "species": "Karenia",
            "cell_concentration": karenia,
            "biovolume": karenia * 10,
            "image_count": 2 if karenia else 0,
            "image_numbers": [f"{pid}_00001", f"{pid}_00002"] if karenia else [],
        },
        {
            "species": "Pseudo-nitzschia",
            "cell_concentration": pseudo_nitzschia,
            "biovolume": pseudo_nitzschia * 10,
            "image_count": 1 if pseudo_nitzschia else 0,
            "image_numbers": [f"{pid}_00003"] if pseudo_nitzschia else [],
        },
    ]


def create_bin(dataset, pid, lng, lat, day, karenia, pseudo_nitzschia):
    return Bin.objects.create(
        pid=pid,
        dataset=dataset,
        geom=Point(lng, lat, srid=4326),
        sample_time=datetime.datetime(2026, 8, day, 12, tzinfo=datetime.UTC),
        cell_concentration_data=concentration_data(karenia, pseudo_nitzschia, pid),
    )


@pytest.fixture
def bins(dataset, target_species, ifcb_metrics):
    # two Bins that snap to the 0.5 degree grid square at (-70, 44), geohash "dry4r",
    # and one Bin in a different square
    return [
        create_bin(dataset, "D20260810T120000_IFCB1", -70.1, 43.9, 10, 500, 100),
        create_bin(dataset, "D20260811T120000_IFCB1", -69.9, 44.1, 11, 300, 0),
        create_bin(dataset, "D20260812T120000_IFCB1", -60.0, 40.0, 12, 0, 50),
    ]


def get_metric(data, metric_id):
    return next(metric for metric in data if metric["metricId"] == metric_id)


class TestTargetSpecies:
    def test_list(self, api_client, target_species):
        response = api_client.get("/api/v1/core/target-species/")

        assert response.status_code == 200
        names = {species["displayName"] for species in response.json()}
        assert names == {"Karenia", "Pseudo-nitzschia"}


class TestDatasets:
    def test_list(self, api_client, bins, dataset):
        response = api_client.get("/api/v1/ifcb-datasets/", DATE_PARAMS)

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "FeatureCollection"
        feature = data["features"][0]
        assert feature["properties"]["dashboardIdName"] == "harpswell"
        assert feature["geometry"]["coordinates"] == [-70.0, 44.0]

    def test_detail_timeseries(self, api_client, bins, dataset):
        response = api_client.get(f"/api/v1/ifcb-datasets/{dataset.id}/", DATE_PARAMS)

        assert response.status_code == 200
        timeseries = {
            item["species"]: item["data"]
            for item in response.json()["properties"]["timeseriesData"]
        }
        karenia_values = sorted(
            get_metric(point["metrics"], "cell_concentration")["value"]
            for point in timeseries["Karenia"]
        )
        assert karenia_values == [0, 300, 500]


class TestBins:
    def test_list(self, api_client, bins):
        response = api_client.get("/api/v1/ifcb-bins/", DATE_PARAMS)

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "FeatureCollection"
        # newest first
        pids = [feature["properties"]["pid"] for feature in data["features"]]
        assert pids == [
            "D20260812T120000_IFCB1",
            "D20260811T120000_IFCB1",
            "D20260810T120000_IFCB1",
        ]

    def test_list_excludes_bins_outside_date_range(self, api_client, bins):
        response = api_client.get(
            "/api/v1/ifcb-bins/", {"start_date": "2026-08-11", "end_date": "2026-08-11"}
        )

        pids = [feature["properties"]["pid"] for feature in response.json()["features"]]
        assert pids == ["D20260811T120000_IFCB1"]

    def test_retrieve(self, api_client, bins):
        response = api_client.get("/api/v1/ifcb-bins/D20260810T120000_IFCB1/", DATE_PARAMS)

        assert response.status_code == 200
        properties = response.json()["properties"]
        assert properties["pid"] == "D20260810T120000_IFCB1"
        karenia = next(
            item
            for item in properties["cellConcentrationData"]
            if item["species"] == "Karenia"
        )
        assert karenia["cellConcentration"] == 500

    def test_species_images(self, api_client, bins):
        response = api_client.get(
            "/api/v1/ifcb-bins/D20260810T120000_IFCB1/get_species_images/",
            dict(DATE_PARAMS, species="Karenia"),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "Karenia"
        assert data["bin"]["datasetId"] == "harpswell"
        # the Dataset's public dashboard URL is used for the image links
        assert data["images"] == [
            "https://ifcb.example.org/harpswell/D20260810T120000_IFCB1_00001.png",
            "https://ifcb.example.org/harpswell/D20260810T120000_IFCB1_00002.png",
        ]


class TestSpatialGrid:
    params = dict(DATE_PARAMS, grid_level="0.5")

    def test_list(self, api_client, bins):
        response = api_client.get("/api/v1/ifcb-spatial-grid/", self.params)

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "FeatureCollection"
        squares = {feature["id"]: feature for feature in data["features"]}
        assert len(squares) == 2

        square = squares["dry4r"]
        assert square["geometry"]["coordinates"] == [-70.0, 44.0]
        values = {
            item["species"]: get_metric(item["data"], "cell_concentration")
            for item in square["properties"]["maxMeanValues"]
        }
        assert values["Karenia"]["maxValue"] == 500
        assert float(values["Karenia"]["meanValue"]) == 400
        assert values["Pseudo-nitzschia"]["maxValue"] == 100
        assert float(values["Pseudo-nitzschia"]["meanValue"]) == 50

    def test_detail(self, api_client, bins):
        response = api_client.get("/api/v1/ifcb-spatial-grid/dry4r/", self.params)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "dry4r"
        timeseries = {
            item["species"]: item["data"]
            for item in data["properties"]["timeseriesData"]
        }
        pids = sorted(point["binPid"] for point in timeseries["Karenia"])
        assert pids == ["D20260810T120000_IFCB1", "D20260811T120000_IFCB1"]
