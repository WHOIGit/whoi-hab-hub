import pytest

from habhub.ifcb_datasets.opensearch import SCORES_INDEX_NAME, SUMMARY_INDEX_NAME

pytestmark = pytest.mark.django_db

DATE_PARAMS = {"start_date": "2026-08-01", "end_date": "2026-08-31"}


def species_result(value=0, image_count=0, models_agreed=0, models=None):
    # binResult() result for a species
    result = {"value": value, "imageCount": image_count, "modelsAgreed": models_agreed}
    if models is not None:
        result["models"] = models
    return result


def bin_hit(pid, sample_time, lat, lng, species, models_run=3, models_required=2, dataset="harpswell"):
    # summary index hit, doc values and the binResult() script field
    return {
        "fields": {
            "binPid": [pid],
            "datasetId": [dataset],
            "mlAnalyzed": [4.170000076293945],
            "modelIds": ["modelA", "modelB", "modelC"][:models_run],
            "point": [f"{lat}, {lng}"],
            "sampleTime": [sample_time],
            "binResult": [
                {
                    "modelsRun": models_run,
                    "modelsRequired": models_required,
                    "species": species,
                }
            ],
        },
        "sort": [pid],
    }


def hits(*items):
    return {"hits": {"hits": list(items)}}


def script_params(search):
    return search["body"]["aggs"]["grid"]["scripted_metric"]["params"]


class TestSpatialGridList:
    url = "/api/v2/ifcb-spatial-grid/"

    @pytest.fixture
    def grid_response(self, fake_opensearch, target_species):
        # one grid square at (-70, 44), keys are the grid point indexes for 0.5 degrees
        fake_opensearch.responses[SUMMARY_INDEX_NAME] = {
            "aggregations": {
                "grid": {
                    "value": {
                        "-140|88": {
                            "bins": 4,
                            "singleModelBins": 1,
                            "minModelsRun": 1,
                            "maxModelsRun": 3,
                            "species": {
                                "Karenia": {"max": 500, "sum": 800, "modelsAgreed": 2, "modelsRun": 3},
                                "Pseudo-nitzschia": {"max": 0, "sum": 0, "modelsAgreed": 0, "modelsRun": 0},
                            },
                        }
                    }
                }
            }
        }
        return fake_opensearch

    def test_response(self, api_client, grid_response):
        response = api_client.get(self.url, dict(DATE_PARAMS, grid_level="0.5"))

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert data["metadata"]["scoreThresholds"] == [
            {"species": "Karenia", "scoreThreshold": 0.95},
            {"species": "Pseudo-nitzschia", "scoreThreshold": 0.5},
        ]
        feature = data["features"][0]
        assert feature["id"] == "dry4r"
        assert feature["geometry"]["coordinates"] == [-70.0, 44.0]
        karenia = feature["properties"]["maxMeanValues"][0]
        assert karenia["species"] == "Karenia"
        assert karenia["data"][0] == {
            "metricId": "cell_concentration",
            "metricName": "Cell Concentration",
            "maxValue": 500,
            # mean over all 4 Bins in the square, Bins without the species count as 0
            "meanValue": 200.0,
            "units": "cells/L",
            "modelsAgreed": 2,
            "modelsRun": 3,
        }
        assert feature["properties"]["modelAgreement"] == {
            "agreement": "majority",
            "binCount": 4,
            "singleModelBinCount": 1,
            "minModelsRun": 1,
            "maxModelsRun": 3,
        }

    def test_query_uses_species_thresholds(self, api_client, grid_response):
        api_client.get(self.url, dict(DATE_PARAMS, grid_level="0.25"))

        search = grid_response.searches_for(SUMMARY_INDEX_NAME)[0]
        assert script_params(search) == {
            "species": ["Karenia", "Pseudo-nitzschia"],
            # threshold * 100, from TargetSpecies.autoclass_threshold
            "minBuckets": {"Karenia": 95, "Pseudo-nitzschia": 50},
            "agreement": "majority",
            "gridLevel": 0.25,
        }
        must = search["body"]["query"]["bool"]["must"]
        assert {"range": {"sampleTime": {"gte": "2026-08-01", "lte": "2026-08-31"}}} in must

    def test_query_params_override_defaults(self, api_client, grid_response):
        api_client.get(
            self.url,
            dict(DATE_PARAMS, score_gte="0.7", agreement="any", model_id="modelA,modelB"),
        )

        params = script_params(grid_response.searches_for(SUMMARY_INDEX_NAME)[0])
        assert params["minBuckets"] == {"Karenia": 70, "Pseudo-nitzschia": 70}
        assert params["agreement"] == "any"
        assert params["models"] == ["modelA", "modelB"]

    def test_species_param(self, api_client, grid_response):
        response = api_client.get(self.url, dict(DATE_PARAMS, species="Karenia"))

        params = script_params(grid_response.searches_for(SUMMARY_INDEX_NAME)[0])
        assert params["species"] == ["Karenia"]
        species = [item["species"] for item in response.json()["features"][0]["properties"]["maxMeanValues"]]
        assert species == ["Karenia"]

    def test_invalid_agreement(self, api_client, grid_response):
        response = api_client.get(self.url, dict(DATE_PARAMS, agreement="most"))

        assert response.status_code == 400
        assert "agreement" in response.json()

    def test_empty_results(self, api_client, fake_opensearch, target_species):
        fake_opensearch.responses[SUMMARY_INDEX_NAME] = {"aggregations": {"grid": {"value": {}}}}

        response = api_client.get(self.url, DATE_PARAMS)

        assert response.status_code == 200
        assert response.json()["features"] == []


class TestSpatialGridDetail:
    url = "/api/v2/ifcb-spatial-grid/dry4r/"

    @pytest.fixture
    def detail_response(self, fake_opensearch, target_species):
        karenia = species_result(500, 2, 2)
        none = species_result()
        fake_opensearch.responses[SUMMARY_INDEX_NAME] = hits(
            bin_hit("BIN2", "2026-08-11T12:00:00Z", 44.1, -69.9, {"Karenia": none, "Pseudo-nitzschia": none}),
            bin_hit("BIN1", "2026-08-10T12:00:00Z", 43.9, -70.1, {"Karenia": karenia, "Pseudo-nitzschia": none}),
            # inside the padded bounding box, but snaps to a different grid square
            bin_hit("BIN3", "2026-08-12T12:00:00Z", 44.3, -70.1, {"Karenia": karenia, "Pseudo-nitzschia": none}),
        )
        return fake_opensearch

    def test_response(self, api_client, detail_response):
        response = api_client.get(self.url, DATE_PARAMS)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "dry4r"
        assert data["geometry"]["coordinates"] == [-70.0, 44.0]
        karenia = data["properties"]["timeseriesData"][0]
        assert karenia["species"] == "Karenia"
        # Bins in the square, ordered by sample time
        assert [point["binPid"] for point in karenia["data"]] == ["BIN1", "BIN2"]
        assert karenia["data"][0] == {
            "sampleTime": "2026-08-10T12:00:00Z",
            "binPid": "BIN1",
            # each Bin's location, to tell fixed and moving platforms apart
            "latitude": 43.9,
            "longitude": -70.1,
            "metrics": [
                {
                    "metricId": "cell_concentration",
                    "metricName": "Cell Concentration",
                    "value": 500,
                    "units": "cells/L",
                }
            ],
            "modelsAgreed": 2,
            "modelsRun": 3,
            "modelsRequired": 2,
        }

    def test_query_bounding_box(self, api_client, detail_response):
        api_client.get(self.url, dict(DATE_PARAMS, grid_level="0.5"))

        must = detail_response.searches_for(SUMMARY_INDEX_NAME)[0]["body"]["query"]["bool"]["must"]
        bbox = next(clause for clause in must if "geo_bounding_box" in clause)
        box = bbox["geo_bounding_box"]["point"]
        assert box["bottom_left"] == pytest.approx([-70.25, 43.75], abs=0.001)
        assert box["top_right"] == pytest.approx([-69.75, 44.25], abs=0.001)

    def test_invalid_geohash(self, api_client, detail_response):
        assert api_client.get("/api/v2/ifcb-spatial-grid/ab!!c/", DATE_PARAMS).status_code == 404

    def test_square_without_bins(self, api_client, fake_opensearch, target_species):
        assert api_client.get(self.url, DATE_PARAMS).status_code == 404


class TestBins:
    @pytest.fixture
    def bin_responses(self, fake_opensearch, target_species, dataset):
        karenia = species_result(4317, 18, 2, models=["modelA", "modelB"])
        none = species_result(models=[])
        bins = [
            bin_hit("BIN1", "2026-08-10T12:00:00Z", 43.9, -70.1, {"Karenia": karenia, "Pseudo-nitzschia": none}),
            bin_hit("BIN2", "2026-08-11T12:00:00Z", 44.1, -69.9, {"Karenia": none, "Pseudo-nitzschia": none}, dataset="mvco"),
        ]

        def summary_response(body):
            # the detail views look up one Bin by pid
            terms = [clause["term"]["binPid"] for clause in body["query"]["bool"]["must"] if "binPid" in clause.get("term", {})]
            return hits(*(item for item in bins if not terms or item["fields"]["binPid"][0] in terms))

        fake_opensearch.responses[SUMMARY_INDEX_NAME] = summary_response

        def image(pid, model, score):
            return {"fields": {"imagePid": [pid], "species": ["Karenia"], "modelId": [model], "score": [score]}}

        fake_opensearch.responses[SCORES_INDEX_NAME] = hits(
            image("BIN1_00001", "modelA", 0.96),
            image("BIN1_00002", "modelA", 0.99),
            image("BIN1_00003", "modelA", 0.96),
            image("BIN1_00003", "modelB", 0.97),
        )
        return fake_opensearch

    def test_list(self, api_client, bin_responses, dataset):
        response = api_client.get("/api/v2/ifcb-bins/", DATE_PARAMS)

        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["agreement"] == "majority"
        # newest first
        assert [feature["id"] for feature in data["features"]] == ["BIN2", "BIN1"]
        properties = data["features"][1]["properties"]
        assert properties["pid"] == "BIN1"
        # the HABhub Dataset id, None for Datasets that aren't in the database
        assert properties["dataset"] == dataset.id
        assert data["features"][0]["properties"]["dataset"] is None
        assert properties["mlAnalyzed"] == 4.17
        assert properties["speciesFound"] == ["Karenia"]
        assert properties["cellConcentrationData"][0] == {
            "species": "Karenia",
            "cellConcentration": 4317,
            "imageCount": 18,
            "modelsAgreed": 2,
        }
        # images are only fetched in the detail view
        assert not bin_responses.searches_for(SCORES_INDEX_NAME)

    def test_retrieve(self, api_client, bin_responses):
        # date params don't apply to a single Bin
        response = api_client.get("/api/v2/ifcb-bins/BIN1/", {"start_date": "2020-01-01"})

        assert response.status_code == 200
        summary_query = bin_responses.searches_for(SUMMARY_INDEX_NAME)[0]["body"]["query"]
        assert summary_query == {"bool": {"must": [{"term": {"binPid": "BIN1"}}]}}

        properties = response.json()["properties"]
        karenia, pseudo_nitzschia = properties["cellConcentrationData"]
        # most models first, then highest score
        assert karenia["imageNumbers"] == ["BIN1_00003", "BIN1_00002", "BIN1_00001"]
        assert pseudo_nitzschia["imageNumbers"] == []
        assert properties["agreement"] == "majority"

    def test_retrieve_image_query(self, api_client, bin_responses):
        api_client.get("/api/v2/ifcb-bins/BIN1/")

        query = bin_responses.searches_for(SCORES_INDEX_NAME)[0]["body"]["query"]["bool"]
        assert query["must"] == [{"term": {"binPid": "BIN1"}}]
        # only species found by enough models, from the models that agreed, with a
        # score threshold matching the histogram buckets
        assert query["should"] == [
            {
                "bool": {
                    "must": [
                        {"term": {"species": "Karenia"}},
                        {"terms": {"modelId": ["modelA", "modelB"]}},
                        {"range": {"score": {"gte": (95 - 0.0001) / 100}}},
                    ]
                }
            }
        ]

    def test_retrieve_unknown_bin(self, api_client, fake_opensearch, target_species):
        assert api_client.get("/api/v2/ifcb-bins/NOT_A_BIN/").status_code == 404

    def test_species_images(self, api_client, bin_responses):
        response = api_client.get("/api/v2/ifcb-bins/BIN1/get_species_images/", {"species": "Karenia"})

        assert response.status_code == 200
        data = response.json()
        assert data["bin"] == {
            "pid": "BIN1",
            "datasetId": "harpswell",
            "datasetLink": "https://ifcb.example.org",
        }
        assert data["species"] == "Karenia"
        assert data["images"] == [
            "https://ifcb.example.org/harpswell/BIN1_00003.png",
            "https://ifcb.example.org/harpswell/BIN1_00002.png",
            "https://ifcb.example.org/harpswell/BIN1_00001.png",
        ]
        assert data["imageTotal"] == 3
        assert data["modelsAgreed"] == 2

    def test_species_images_limit(self, api_client, bin_responses):
        bin_responses.responses[SCORES_INDEX_NAME] = hits(
            *(
                {"fields": {"imagePid": [f"BIN1_{n:05}"], "species": ["Karenia"], "modelId": ["modelA"], "score": [0.99]}}
                for n in range(35)
            )
        )

        data = api_client.get("/api/v2/ifcb-bins/BIN1/get_species_images/", {"species": "Karenia"}).json()

        assert len(data["images"]) == 30
        assert data["imageTotal"] == 35

    def test_species_images_default_dashboard(self, api_client, bin_responses):
        # BIN2's Dataset isn't in the HABhub database
        data = api_client.get("/api/v2/ifcb-bins/BIN2/get_species_images/", {"species": "Karenia"}).json()

        assert data["bin"]["datasetLink"] == "https://habon-ifcb.whoi.edu"

    def test_species_images_unknown_species(self, api_client, bin_responses):
        response = api_client.get("/api/v2/ifcb-bins/BIN1/get_species_images/", {"species": "Unknown"})

        assert response.status_code == 400


class TestFixedMetrics:
    url = "/api/v2/ifcb-fixed-metrics/"

    def test_missing_params(self, api_client, fake_opensearch):
        response = api_client.get(self.url)

        assert response.status_code == 400

    def test_unknown_dataset(self, api_client, fake_opensearch):
        response = api_client.get(self.url, {"dataset_id": "unknown", "species": "Karenia"})

        assert response.status_code == 404

    def test_cell_concentration(self, api_client, fake_opensearch, dataset):
        fake_opensearch.responses[SCORES_INDEX_NAME] = {
            "aggregations": {
                "species-agg": {
                    "buckets": [
                        {
                            "key": "Karenia",
                            "bin-agg": {
                                "buckets": [
                                    {
                                        "key": "BIN1",
                                        "doc_count": 10,
                                        "mlAnalyzed": {"value": 5.0},
                                        "hits": {
                                            "hits": {
                                                "hits": [
                                                    {
                                                        "_source": {
                                                            "sampleTime": "2026-08-10T12:00:00Z",
                                                            "mlAnalyzed": 5.0,
                                                            "point": [-70.1, 43.9],
                                                        }
                                                    }
                                                ]
                                            }
                                        },
                                    }
                                ]
                            },
                        }
                    ]
                }
            }
        }

        response = api_client.get(self.url, {"dataset_id": "harpswell", "species": "Karenia"})

        assert response.status_code == 200
        timeseries = response.json()["properties"]["timeseriesData"]
        assert timeseries[0]["species"] == "Karenia"
        point = timeseries[0]["data"][0]
        assert point["binPid"] == "BIN1"
        # 10 images / 5 mL * 1000
        assert point["metrics"][0]["value"] == 2000


class TestSpeciesScores:
    def test_list(self, api_client, fake_opensearch):
        fake_opensearch.responses[SCORES_INDEX_NAME] = {
            "hits": {
                "total": {"value": 1},
                "hits": [{"_source": {"binPid": "BIN1", "species": "Karenia", "score": 0.97}, "sort": [1786363200000]}],
            }
        }

        response = api_client.get("/api/v2/ifcb-species-scores/", {"species": "Karenia"})

        assert response.status_code == 200
        data = response.json()
        assert data["totalHits"] == 1
        assert data["page"] == 1
        assert data["links"] == {"next": None, "previous": None}
        # the camelCase renderer turns Opensearch's "_source" into "Source"
        assert data["results"][0]["Source"]["binPid"] == "BIN1"


class TestBinLocations:
    url = "/api/v2/ifcb-bin-locations/"

    @staticmethod
    def location(tile, lat, lng, bin_count, datasets, start, end):
        # composite aggregation bucket for a location
        return {
            "key": {"tile": tile},
            "doc_count": bin_count,
            "point": {"location": {"lat": lat, "lon": lng}},
            "start": {"value_as_string": start},
            "end": {"value_as_string": end},
            "datasets": {"buckets": [{"key": dataset} for dataset in datasets]},
        }

    def test_response(self, api_client, fake_opensearch):
        fake_opensearch.responses[SUMMARY_INDEX_NAME] = {
            "aggregations": {
                "locations": {
                    "buckets": [
                        self.location("29/1/1", 43.7921140001, -69.9578820001, 120, ["harpswell"], "2026-08-01T00:00:00.000Z", "2026-08-30T00:00:00.000Z"),
                        self.location("29/2/2", 41.5, -70.5, 1, ["mvco"], "2026-08-10T12:00:00.000Z", "2026-08-10T12:00:00.000Z"),
                    ]
                }
            }
        }

        response = api_client.get(self.url, DATE_PARAMS)

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert data["metadata"] == {"locationCount": 2, "binCount": 121}
        assert data["features"][0] == {
            "type": "Feature",
            "id": "29/1/1",
            "geometry": {"type": "Point", "coordinates": [-69.957882, 43.792114]},
            "properties": {
                "binCount": 120,
                "datasetIds": ["harpswell"],
                "startTime": "2026-08-01T00:00:00.000Z",
                "endTime": "2026-08-30T00:00:00.000Z",
            },
        }

    def test_query(self, api_client, fake_opensearch):
        api_client.get(self.url, dict(DATE_PARAMS, dataset_id="harpswell", species="Karenia"))

        search = fake_opensearch.searches_for(SUMMARY_INDEX_NAME)[0]
        must = search["body"]["query"]["bool"]["must"]
        assert {"range": {"sampleTime": {"gte": "2026-08-01", "lte": "2026-08-31"}}} in must
        assert {"terms": {"datasetId": ["harpswell"]}} in must
        # species is an image level filter, every Bin location is returned
        assert not any("species" in clause.get("terms", {}) for clause in must)
        composite = search["body"]["aggs"]["locations"]["composite"]
        assert composite["sources"] == [{"tile": {"geotile_grid": {"field": "point", "precision": 29}}}]
        # only the fields needed are returned
        assert "aggregations.locations.after_key" in search["kwargs"]["filter_path"]

    def test_pages_through_locations(self, api_client, fake_opensearch, monkeypatch):
        from habhub.ifcb_datasets.api2.views import IfcbBinLocationsViewSet

        monkeypatch.setattr(IfcbBinLocationsViewSet, "locations_page_size", 1)
        pages = [
            {"aggregations": {"locations": {"after_key": {"tile": "29/1/1"}, "buckets": [self.location("29/1/1", 44, -70, 5, ["a"], "t1", "t2")]}}},
            {"aggregations": {"locations": {"after_key": {"tile": "29/2/2"}, "buckets": [self.location("29/2/2", 41, -70, 3, ["b"], "t1", "t2")]}}},
            {"aggregations": {"locations": {"buckets": []}}},
        ]
        fake_opensearch.responses[SUMMARY_INDEX_NAME] = lambda body: pages[len(fake_opensearch.searches) - 1]

        data = api_client.get(self.url, DATE_PARAMS).json()

        assert [feature["id"] for feature in data["features"]] == ["29/1/1", "29/2/2"]
        searches = fake_opensearch.searches_for(SUMMARY_INDEX_NAME)
        assert len(searches) == 3
        assert searches[1]["body"]["aggs"]["locations"]["composite"]["after"] == {"tile": "29/1/1"}
