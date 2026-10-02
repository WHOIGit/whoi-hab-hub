import datetime
import environ
import urllib.parse
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth, helpers
from requests_aws4auth import AWS4Auth

from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.db.models import Q
from django.urls import reverse
from rest_framework import status, viewsets
from rest_framework.decorators import action

# from rest_framework.reverse import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_gis.fields import GeometryField
from .mixins import ScoresFiltersMixin
from ..models import Dataset
from ..api.cache_utils import create_cache_key
from ..opensearch import (
    SCORES_INDEX_NAME,
    SUMMARY_INDEX_NAME,
    BIN_RESULT_SCRIPT,
    GRID_INIT_SCRIPT,
    GRID_MAP_SCRIPT,
    GRID_COMBINE_SCRIPT,
    GRID_REDUCE_SCRIPT,
)
from habhub.core.constants import API_URL
from habhub.core.models import TargetSpecies, Metric

env = environ.Env()

AWS_ACCESS_KEY_ID = env("DJANGO_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("DJANGO_AWS_SECRET_ACCESS_KEY")


def connect_opensearch():
    # Connect to OS for indexing
    host = "search-habhub-production-li4bxtldklbdlnyv6kuav3p4kq.us-east-1.es.amazonaws.com"  # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
    region = "us-east-1"
    service = "es"
    awsauth = AWS4Auth(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, region, service)

    try:
        os_client = OpenSearch(
            hosts=[{"host": host, "port": 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            pool_maxsize=20,
            timeout=20,
            # gzip requests/responses, the spatial grid responses are several MB
            http_compress=True,
        )
        print("Connect to OS", os_client)
        info = os_client.info()
        print(os_client.info())
        print(f"Welcome to {info['version']['number']}!")

    except Exception as err:
        print("Connection error", err)
        return Response(
            {
                "statusCode": 400,
                "body": "Error Connecting",
            }
        )

    return os_client


# API view to return base species score resutls from AWS Opensearch
class SpeciesScoresIndexViewSet(ScoresFiltersMixin, viewsets.ViewSet):
    def list(self, request):
        os_client = connect_opensearch()
        index_name = "species-scores"

        # set up initial pagination options
        per_page = 100  # result per page returned by OS
        query_params = request.query_params.dict()
        query_params.pop("search_after", None)
        query_params.pop("page", None)
        relative_link = reverse("api_v2:ifcb-species-scores-list")
        print("link", relative_link)
        link = f"{API_URL}{relative_link}"
        print(link)
        uri = f"{link}?{urllib.parse.urlencode(query_params)}"

        current_page = int(request.query_params.get("page", 1))
        prev_page = current_page - 1
        next_page = current_page + 1

        current_search_after = request.query_params.get("search_after", None)

        prev_link = None
        next_link = None

        # build the query
        # filter the query parameters
        query = self.handle_query_param_filters()
        # add sorting
        sort = [
            {
                "sampleTime": {
                    "order": "asc",
                }
            }
        ]

        query["sort"] = sort

        try:
            # search the DB
            # use search_after to paginate through all results
            print("search the DB", os_client)
            response = os_client.search(body=query, index=index_name, size=100)
            # print(response)
            results = response["hits"]["hits"]
            total_hits = response["hits"]["total"]["value"]
            # create next/prev link using the "sort" value from OS
            last_element = response["hits"]["hits"][-1]

            next_sort = last_element["sort"][0]

            print(last_element, next_sort)

            if current_page == 1:
                prev_link = None
            elif current_page == 2:
                prev_link = uri
            else:
                prev_link = (
                    f"{uri}&search_after={current_search_after}&page={prev_page}"
                )

            if len(results) < per_page:
                next_link = None
            else:
                next_link = f"{uri}&search_after={next_sort}&page={next_page}"

            # use scan to get more than 10000 responses
            # response = helpers.scan(
            #    os_client, index=index_name, scroll="10m", size=1000, query=query
            # )
            # data = list(response)

            api_response = {
                "links": {
                    "next": next_link,
                    "previous": prev_link,
                },
                "totalHits": total_hits,
                "page": current_page,
                "results": results,
            }
        except Exception as err:
            print("Search error", err)
            return Response(
                {
                    "statusCode": 400,
                    "body": "Error Running Query",
                }
            )

        return Response(api_response)


# API view to return species scorer resutls from AWS Opensearch
class IfcbFixedMetricsViewSet(ScoresFiltersMixin, viewsets.ViewSet):
    def list(self, request):
        os_client = connect_opensearch()
        index_name = "species-scores"

        # validate we have a dataset and species
        dataset_id = self.request.query_params.get("dataset_id", None)
        species = self.request.query_params.get("species", None)

        missing_params = [
            name
            for name, value in (("dataset_id", dataset_id), ("species", species))
            if not value
        ]
        if missing_params:
            return Response(
                {
                    "statusCode": 400,
                    "body": f"Missing required parameter(s): {', '.join(missing_params)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        species_list = species.split(",")

        # get the Dataset
        dataset = Dataset.objects.filter(dashboard_id_name=dataset_id).first()
        if not dataset:
            return Response(
                {
                    "statusCode": 404,
                    "body": f"Dataset not found: {dataset_id}",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # build the query
        query = self.handle_query_param_filters()
        # add aggregation, bucket by species first so each species gets its own bin counts
        agg = {
            "species-agg": {
                "terms": {"field": "species", "size": len(species_list)},
                "aggs": {
                    "bin-agg": {
                        "terms": {"field": "binPid", "size": 10000},
                        "aggs": {
                            "mlAnalyzed": {"max": {"field": "mlAnalyzed"}},
                            "hits": {
                                "top_hits": {
                                    "_source": ["sampleTime", "mlAnalyzed", "point"],
                                    "size": 1,
                                }
                            },
                        },
                    },
                },
            },
        }

        # working example with script
        """
        agg = {
            "bin-agg": {
                "terms": {"field": "binPid", "size": 10000},
                "aggs": {
                    "mlAnalyzed": {"max": {"field": "mlAnalyzed"}},
                    "cell-concentration": {
                        "bucket_script": {
                            "buckets_path": {
                                "binCount": "_count",
                                "mlAnalyzed": "mlAnalyzed",
                            },
                            "script": "Math.round(params.binCount / params.mlAnalyzed * 1000)/1",
                        }
                    },
                },
            },
        }
        """
        query["aggs"] = agg
        # set size
        query["size"] = 0
        print(query)
        try:
            # search the DB
            response = os_client.search(body=query, index=index_name)

        except Exception as err:
            print(err)
            return Response(
                {
                    "statusCode": 400,
                    "body": "Error Running Query",
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        species_buckets = {
            bucket["key"]: bucket["bin-agg"]["buckets"]
            for bucket in response["aggregations"]["species-agg"]["buckets"]
        }

        # parse OpenSearch response
        timeseries_data = []
        for species in species_list:
            species_item = {
                "species": species,
                "species_display": species.replace("_", " "),
            }
            timeseries_data.append(species_item)

            data = []
            for item in species_buckets.get(species, []):
                os_data = item["hits"]["hits"]["hits"][0]["_source"]
                print(os_data)
                data_item = {
                    "bin_pid": item["key"],
                    "sample_time": os_data["sampleTime"],
                    "point": os_data["point"],
                }
                metrics = []
                cell_concentration = {
                    "metricId": "cell_concentration",
                    "metricName": "Cell Concentration",
                    "value": round(
                        item["doc_count"] / item["mlAnalyzed"]["value"] * 1000
                    ),
                    "units": "cells/L",
                }
                metrics.append(cell_concentration)
                data_item["metrics"] = metrics

                data.append(data_item)

            species_item["data"] = data

        # build the GeoJSON response
        geojson = OrderedDict()
        # required type attribute
        # must be "Feature" according to GeoJSON spec
        geojson["id"] = dataset.id
        geojson["type"] = "Feature"
        geo_field = GeometryField()
        geojson["geometry"] = geo_field.to_representation(dataset.geom)
        # set GeoJSON properties
        properties = OrderedDict()
        properties["timeseries_data"] = timeseries_data

        print(geojson)
        """
        for k, v in data.items():
            if k != "features":
                metadata[k] = data[k]
        """
        # required features attribute
        # MUST be present in output according to GeoJSON spec
        geojson["properties"] = properties

        return Response(geojson)


GEOHASH_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def encode_geohash(lat, lng, precision=5):
    # pure Python equivalent of PostGIS ST_GeoHash() so grid square IDs match the
    # v1 "ifcb-spatial-grid" endpoint
    lat_range = [-90.0, 90.0]
    lng_range = [-180.0, 180.0]
    geohash = []
    bits = 0
    bit_count = 0
    is_lng = True

    while len(geohash) < precision:
        value_range, value = (lng_range, lng) if is_lng else (lat_range, lat)
        mid = (value_range[0] + value_range[1]) / 2
        if value >= mid:
            bits = (bits << 1) | 1
            value_range[0] = mid
        else:
            bits = bits << 1
            value_range[1] = mid

        is_lng = not is_lng
        bit_count += 1
        if bit_count == 5:
            geohash.append(GEOHASH_BASE32[bits])
            bits = 0
            bit_count = 0

    return "".join(geohash)


def decode_geohash_center(geohash):
    # return the (lat, lng) center point of a Geohash cell, None if it's invalid
    lat_range = [-90.0, 90.0]
    lng_range = [-180.0, 180.0]
    is_lng = True

    for char in geohash:
        if char not in GEOHASH_BASE32:
            return None
        bits = GEOHASH_BASE32.index(char)
        for shift in range(4, -1, -1):
            value_range = lng_range if is_lng else lat_range
            mid = (value_range[0] + value_range[1]) / 2
            if bits >> shift & 1:
                value_range[0] = mid
            else:
                value_range[1] = mid
            is_lng = not is_lng

    return (lat_range[0] + lat_range[1]) / 2, (lng_range[0] + lng_range[1]) / 2


def snap_to_grid(value, grid_level):
    # same rounding as PostGIS ST_SnapToGrid()
    return round(value / grid_level) * grid_level


# Query param options and Opensearch queries shared by the v2 views that use the
# per-Bin "bin-species-summary" index. A species is only counted as present in a Bin
# if enough of the ML models run on the Bin agree, set by the `agreement` param:
#   all:      every model run on the Bin found the species
#   majority: more than half of the models found it (default)
#   any:      at least one model found it
# A single model run on a Bin counts for all three. The number of models that
# agreed/ran is returned with the results so clients can show lower confidence data.
# Images are only counted if their score is >= the species' TargetSpecies.autoclass_threshold
# (or the `score_gte` param), applied at query time from the per-Bin score histograms.
# The model agreement rule is in Opensearch scripts, see binResult() in
# ifcb_datasets/opensearch.py.
class ModelAgreementMixin(ScoresFiltersMixin):
    agreement_options = ("all", "majority", "any")
    default_agreement = "majority"
    # number of documents to return per page, max allowed by Opensearch
    bins_page_size = 10000
    cache_timeout = 60 * 60

    def get_options(self):
        # parse the query params for the model agreement and species
        query_params = self.request.query_params

        agreement = query_params.get("agreement", self.default_agreement)
        if agreement not in self.agreement_options:
            raise ValidationError(
                {"agreement": f"Must be one of: {', '.join(self.agreement_options)}"}
            )

        species_param = query_params.get("species", None)
        species_list = list(
            TargetSpecies.objects.values_list(
                "species_id", "display_name", "autoclass_threshold"
            )
        )
        if species_param:
            requested_species = species_param.split(",")
            species_list = [s for s in species_list if s[0] in requested_species]

        # score threshold for each species, the score_gte param overrides the
        # TargetSpecies thresholds for all species
        try:
            score_gte = float(query_params["score_gte"])
        except (KeyError, ValueError):
            score_gte = None
        score_thresholds = {
            species_id: score_gte if score_gte is not None else float(threshold)
            for species_id, _, threshold in species_list
        }

        model_param = query_params.get("model_id", None)

        metric = Metric.objects.filter(metric_id="cell_concentration").first()

        return {
            "agreement": agreement,
            "species_ids": [species_id for species_id, _, _ in species_list],
            "species_display": {
                species_id: display for species_id, display, _ in species_list
            },
            "score_thresholds": score_thresholds,
            "model_list": model_param.split(",") if model_param else None,
            "metric_name": metric.name if metric else "Cell Concentration",
            "metric_units": metric.units if metric else "cells/L",
        }

    def search_all(self, os_client, index, query):
        # use search_after to page through all results. filter_path only returns
        # the fields needed to keep the response small
        query = dict(query, size=self.bins_page_size, track_total_hits=False)
        hits = []
        while True:
            response = os_client.search(
                body=query,
                index=index,
                request_timeout=60,
                filter_path="hits.hits.sort,hits.hits.fields",
            )
            page = response.get("hits", {}).get("hits", [])
            hits.extend(page)

            if len(page) < self.bins_page_size:
                return hits
            query["search_after"] = page[-1]["sort"]

    def get_bool_query(self, extra_filters=None):
        # Opensearch bool query for the Bins matching the query params
        query = self.handle_query_param_filters()
        # species/model/score are image level filters that don't exist in the summary
        # indexes. Every Bin in the date range is returned so Bins without the species
        # still count as 0, matching the v1 endpoint.
        must = [
            clause
            for clause in query["query"]["bool"]["must"]
            if not {"species", "modelId"} & clause.get("terms", {}).keys()
            and "score" not in clause.get("range", {})
        ] + (extra_filters or [])
        return dict(query["query"]["bool"], must=must)

    def get_script_params(self, options):
        # params for binResult() in ifcb_datasets/opensearch.py
        params = {
            "species": options["species_ids"],
            "minBuckets": {
                species: round(threshold * 100)
                for species, threshold in options["score_thresholds"].items()
            },
            "agreement": options["agreement"],
        }
        # script params can't contain nulls, so only add the model filter if it's set
        if options["model_list"]:
            params["models"] = options["model_list"]
        return params

    def fetch_bins(self, options, extra_filters=None, bool_query=None, include_models=False):
        # return all Bins matching the query params (or bool_query) with their
        # species results, calculated in Opensearch by binResult()
        params = self.get_script_params(options)
        if include_models:
            params["includeModels"] = True
        query = {
            "query": {"bool": bool_query or self.get_bool_query(extra_filters)},
            "sort": [{"binPid": "asc"}],
            "_source": False,
            "docvalue_fields": [
                "binPid",
                "datasetId",
                "mlAnalyzed",
                "modelIds",
                "point",
                {"field": "sampleTime", "format": "strict_date_time_no_millis"},
            ],
            "script_fields": {
                "binResult": {
                    "script": {"source": BIN_RESULT_SCRIPT, "params": params}
                }
            },
        }
        hits = self.search_all(connect_opensearch(), SUMMARY_INDEX_NAME, query)

        bins = []
        for hit in hits:
            fields = hit["fields"]
            result = fields["binResult"][0]
            # skip Bins that can't be placed on the grid or have no volume
            if not result:
                continue
            # geo_point doc values are "lat, lon" strings
            lat, lng = (float(value) for value in fields["point"][0].split(","))
            bins.append(
                {
                    "binPid": fields["binPid"][0],
                    "datasetId": fields.get("datasetId", [None])[0],
                    "sampleTime": fields["sampleTime"][0],
                    "point": [lng, lat],
                    # doc values are float32, round to the original mL value
                    "mlAnalyzed": round(fields["mlAnalyzed"][0], 6),
                    "modelIds": fields.get("modelIds", []),
                    "modelsRun": result["modelsRun"],
                    "modelsRequired": result["modelsRequired"],
                    "species": result["species"],
                }
            )
        return bins

    def format_score_thresholds(self, options):
        # list instead of a dict so the camelCase renderer doesn't change the species IDs
        return [
            {"species": species, "score_threshold": threshold}
            for species, threshold in options["score_thresholds"].items()
        ]

    def error_response(self, err):
        print(err)
        return Response(
            {
                "statusCode": 400,
                "body": "Error Running Query",
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )


# API view to return spatial grid of species cell concentrations from AWS Opensearch.
# Matches the response format of the v1 "ifcb-spatial-grid" endpoint, with the model
# agreement options from ModelAgreementMixin. The list view aggregates the Bins into
# grid squares in Opensearch, the detail view gets each Bin in the grid square.
class IfcbSpatialGridViewSet(ModelAgreementMixin, viewsets.ViewSet):
    default_grid_level = 0.5

    def get_options(self):
        options = super().get_options()
        try:
            grid_level = float(
                self.request.query_params.get("grid_level", self.default_grid_level)
            )
        except ValueError:
            grid_level = self.default_grid_level

        if grid_level <= 0:
            grid_level = self.default_grid_level

        return dict(options, grid_level=grid_level)

    def fetch_grid_squares(self, options):
        # aggregate all Bins matching the query params into grid squares in
        # Opensearch, see GRID_MAP_SCRIPT in ifcb_datasets/opensearch.py
        params = dict(self.get_script_params(options), gridLevel=options["grid_level"])

        query = {
            "size": 0,
            "track_total_hits": False,
            "query": {"bool": self.get_bool_query()},
            "aggs": {
                "grid": {
                    "scripted_metric": {
                        "init_script": GRID_INIT_SCRIPT,
                        "map_script": GRID_MAP_SCRIPT,
                        "combine_script": GRID_COMBINE_SCRIPT,
                        "reduce_script": GRID_REDUCE_SCRIPT,
                        "params": params,
                    }
                }
            },
        }
        response = connect_opensearch().search(
            body=query, index=SUMMARY_INDEX_NAME, request_timeout=60
        )

        # square keys are the grid point as "{lng index}|{lat index}"
        grid_squares = {}
        for key, square in (response["aggregations"]["grid"]["value"] or {}).items():
            lng_index, lat_index = (int(value) for value in key.split("|"))
            grid_point = (
                lng_index * options["grid_level"],
                lat_index * options["grid_level"],
            )
            grid_squares[grid_point] = square
        return grid_squares

    def get_grid_point(self, bin_data, grid_level):
        lng, lat = bin_data["point"]
        return snap_to_grid(lng, grid_level), snap_to_grid(lat, grid_level)

    def list(self, request):
        cache_key = create_cache_key(request)
        cached_data = cache.get(cache_key)
        if cached_data:
            print("CACHE HIT")
            return Response(cached_data)

        options = self.get_options()
        try:
            grid_squares = self.fetch_grid_squares(options)
        except Exception as err:
            return self.error_response(err)

        # build the GeoJSON response
        geo_field = GeometryField()
        features = []
        for (grid_lng, grid_lat), square in sorted(grid_squares.items()):
            max_mean_values = []
            for species in options["species_ids"]:
                result = square["species"][species]
                max_mean_values.append(
                    {
                        "species": species,
                        "data": [
                            {
                                "metric_id": "cell_concentration",
                                "metric_name": options["metric_name"],
                                "max_value": result["max"],
                                # Bins without the species count as 0
                                "mean_value": result["sum"] / square["bins"],
                                "units": options["metric_units"],
                                # model agreement for the Bin with the max value
                                "models_agreed": result["modelsAgreed"],
                                "models_run": result["modelsRun"],
                            }
                        ],
                    }
                )

            feature = OrderedDict()
            # required type attribute
            # must be "Feature" according to GeoJSON spec
            feature["type"] = "Feature"
            # set id to be unique geohash
            feature["id"] = encode_geohash(grid_lat, grid_lng, 5)
            feature["geometry"] = geo_field.to_representation(
                Point(grid_lng, grid_lat, srid=4326)
            )
            properties = OrderedDict()
            properties["max_mean_values"] = max_mean_values
            # summary of model agreement for all Bins in the grid square.
            # single_model_bin_count is the number of Bins only one model ran on,
            # where a species counts without any other model agreeing
            properties["model_agreement"] = {
                "agreement": options["agreement"],
                "bin_count": square["bins"],
                "single_model_bin_count": square["singleModelBins"],
                "min_models_run": square["minModelsRun"],
                "max_models_run": square["maxModelsRun"],
            }
            feature["properties"] = properties
            features.append(feature)

        geojson = OrderedDict()
        # must be "FeatureCollection" according to GeoJSON spec
        geojson["type"] = "FeatureCollection"
        geojson["metadata"] = OrderedDict(
            score_thresholds=self.format_score_thresholds(options)
        )
        # required features attribute
        # MUST be present in output according to GeoJSON spec
        geojson["features"] = features

        cache.set(cache_key, geojson, self.cache_timeout)
        return Response(geojson)

    def retrieve(self, request, pk=None):
        # use the unique Geohash from the list view for the pk lookup
        cache_key = create_cache_key(request, pk)
        cached_data = cache.get(cache_key)
        if cached_data:
            print("CACHE HIT")
            return Response(cached_data)

        options = self.get_options()
        grid_level = options["grid_level"]
        not_found = Response(
            {
                "statusCode": 404,
                "body": f"Grid square not found: {pk}",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

        # find the grid square center point from the Geohash. The Geohash cell is
        # smaller than the grid square, so it contains only one grid point
        center = decode_geohash_center(pk)
        if not center:
            return not_found

        grid_lng = snap_to_grid(center[1], grid_level)
        grid_lat = snap_to_grid(center[0], grid_level)
        if encode_geohash(grid_lat, grid_lng, 5) != pk:
            return not_found

        # get the Bins inside the grid square, pad the edges so Bins on the
        # border are included, then match them exactly by snapping to the grid
        padding = grid_level / 2 + 0.000001
        bbox_filter = {
            "geo_bounding_box": {
                "point": {
                    # keep the box inside valid coordinates
                    "bottom_left": [
                        max(grid_lng - padding, -180),
                        max(grid_lat - padding, -90),
                    ],
                    "top_right": [
                        min(grid_lng + padding, 180),
                        min(grid_lat + padding, 90),
                    ],
                }
            }
        }
        try:
            bins = self.fetch_bins(options, extra_filters=[bbox_filter])
        except Exception as err:
            return self.error_response(err)

        bins = sorted(
            (
                bin_data
                for bin_data in bins
                if self.get_grid_point(bin_data, grid_level) == (grid_lng, grid_lat)
            ),
            key=lambda bin_data: (bin_data["sampleTime"], bin_data["binPid"]),
        )
        if not bins:
            return not_found

        timeseries_data = [
            {
                "species": species,
                "species_display": options["species_display"][species],
                "data": [],
            }
            for species in options["species_ids"]
        ]

        for bin_data in bins:
            sample_time = datetime.datetime.fromisoformat(bin_data["sampleTime"])
            date_str = sample_time.astimezone(datetime.UTC).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            for species_item in timeseries_data:
                result = bin_data["species"][species_item["species"]]
                species_item["data"].append(
                    {
                        "sample_time": date_str,
                        "bin_pid": bin_data["binPid"],
                        "metrics": [
                            {
                                "metric_id": "cell_concentration",
                                "metric_name": options["metric_name"],
                                # 0 if the species wasn't found by enough models
                                "value": result["value"],
                                "units": options["metric_units"],
                            }
                        ],
                        # number of models that found the species, the number that
                        # ran on the Bin, and the number required to agree
                        "models_agreed": result["modelsAgreed"],
                        "models_run": bin_data["modelsRun"],
                        "models_required": bin_data["modelsRequired"],
                    }
                )

        # build the GeoJSON response
        geojson = OrderedDict()
        # required type attribute
        # must be "Feature" according to GeoJSON spec
        geojson["type"] = "Feature"
        # set id to be unique geohash
        geojson["id"] = pk
        geo_field = GeometryField()
        geojson["geometry"] = geo_field.to_representation(
            Point(grid_lng, grid_lat, srid=4326)
        )
        geojson["properties"] = OrderedDict(
            score_thresholds=self.format_score_thresholds(options),
            timeseries_data=timeseries_data,
        )

        cache.set(cache_key, geojson, self.cache_timeout)
        return Response(geojson)


# IFCB Dashboard used by the ingest Lambda, for image links of Datasets that aren't
# in the HABhub database
DEFAULT_DASHBOARD_URL = "https://habon-ifcb.whoi.edu"


# API view to return IFCB Bin metadata and species results from AWS Opensearch, like
# the v1 "ifcb-bins" endpoint, with the model agreement options from
# ModelAgreementMixin. The detail view also returns the images for each species from
# the image level "species-scores" index, and "get_species_images" returns links to
# a species' images.
class IfcbBinViewSet(ModelAgreementMixin, viewsets.ViewSet):
    # Bin pids are the lookup value
    lookup_value_regex = "[^/]+"
    # the list view returns every Bin, so default to a shorter range than the
    # other views if the start_date param isn't set
    default_date_range = relativedelta(months=1)
    # max number of images returned by get_species_images, same as v1
    images_limit = 30

    def get_datasets(self):
        # HABhub Datasets by IFCB Dashboard ID
        return {dataset.dashboard_id_name: dataset for dataset in Dataset.objects.all()}

    def fetch_bin(self, options, bin_pid):
        # get one Bin by pid, regardless of the date range params
        bins = self.fetch_bins(
            options,
            bool_query={"must": [{"term": {"binPid": bin_pid}}]},
            include_models=True,
        )
        return bins[0] if bins else None

    def fetch_images(self, bin_data, options):
        # return the image pids for each species found in the Bin: the images the
        # agreeing models classified as the species with a score >= its threshold.
        # Images are ordered by the number of models that found them, then their
        # highest score, so the most certain images come first.
        species_filters = []
        for species, result in bin_data["species"].items():
            if not result["value"]:
                continue
            # same as the histogram buckets: bucket = floor(score * 100 + 0.0001)
            min_bucket = round(options["score_thresholds"][species] * 100)
            species_filters.append(
                {
                    "bool": {
                        "must": [
                            {"term": {"species": species}},
                            {"terms": {"modelId": result["models"]}},
                            {"range": {"score": {"gte": (min_bucket - 0.0001) / 100}}},
                        ]
                    }
                }
            )
        if not species_filters:
            return {}

        query = {
            "query": {
                "bool": {
                    "must": [{"term": {"binPid": bin_data["binPid"]}}],
                    "should": species_filters,
                    "minimum_should_match": 1,
                }
            },
            "sort": [{"imagePid": "asc"}, {"modelId": "asc"}],
            "_source": False,
            "docvalue_fields": ["imagePid", "species", "modelId", "score"],
        }
        hits = self.search_all(connect_opensearch(), SCORES_INDEX_NAME, query)

        images = {}
        for hit in hits:
            fields = hit["fields"]
            image = images.setdefault(fields["species"][0], {}).setdefault(
                fields["imagePid"][0], {"models": 0, "score": 0}
            )
            image["models"] += 1
            image["score"] = max(image["score"], fields["score"][0])

        return {
            species: sorted(
                species_images,
                key=lambda pid: (
                    -species_images[pid]["models"],
                    -species_images[pid]["score"],
                    pid,
                ),
            )
            for species, species_images in images.items()
        }

    def build_feature(self, bin_data, options, datasets, images=None):
        # GeoJSON Feature for a Bin, image_numbers are only included in the detail view
        dataset = datasets.get(bin_data["datasetId"])
        cell_concentration_data = []
        for species in options["species_ids"]:
            result = bin_data["species"][species]
            species_data = {
                "species": species,
                "cell_concentration": result["value"],
                "image_count": result["imageCount"],
                "models_agreed": result["modelsAgreed"],
            }
            if images is not None:
                species_data["image_numbers"] = images.get(species, [])
            cell_concentration_data.append(species_data)

        feature = OrderedDict()
        feature["id"] = bin_data["binPid"]
        # required type attribute
        # must be "Feature" according to GeoJSON spec
        feature["type"] = "Feature"
        lng, lat = bin_data["point"]
        feature["geometry"] = GeometryField().to_representation(
            Point(lng, lat, srid=4326)
        )
        properties = OrderedDict()
        properties["pid"] = bin_data["binPid"]
        # HABhub Dataset id like v1, None if the Dataset isn't in the HABhub database
        properties["dataset"] = dataset.id if dataset else None
        properties["dataset_id"] = bin_data["datasetId"]
        properties["sample_time"] = bin_data["sampleTime"]
        properties["ml_analyzed"] = bin_data["mlAnalyzed"]
        properties["model_ids"] = bin_data["modelIds"]
        properties["models_run"] = bin_data["modelsRun"]
        properties["models_required"] = bin_data["modelsRequired"]
        properties["species_found"] = [
            data["species"] for data in cell_concentration_data if data["cell_concentration"]
        ]
        properties["cell_concentration_data"] = cell_concentration_data
        feature["properties"] = properties
        return feature

    def not_found(self, bin_pid):
        return Response(
            {"statusCode": 404, "body": f"Bin not found: {bin_pid}"},
            status=status.HTTP_404_NOT_FOUND,
        )

    def list(self, request):
        # all Bins matching the query params, newest first like v1
        cache_key = create_cache_key(request)
        cached_data = cache.get(cache_key)
        if cached_data:
            print("CACHE HIT")
            return Response(cached_data)

        options = self.get_options()
        try:
            bins = self.fetch_bins(options)
        except Exception as err:
            return self.error_response(err)

        datasets = self.get_datasets()
        bins.sort(key=lambda bin_data: (bin_data["sampleTime"], bin_data["binPid"]), reverse=True)

        geojson = OrderedDict()
        # must be "FeatureCollection" according to GeoJSON spec
        geojson["type"] = "FeatureCollection"
        geojson["metadata"] = OrderedDict(
            agreement=options["agreement"],
            score_thresholds=self.format_score_thresholds(options),
        )
        geojson["features"] = [
            self.build_feature(bin_data, options, datasets) for bin_data in bins
        ]

        cache.set(cache_key, geojson, self.cache_timeout)
        return Response(geojson)

    def retrieve(self, request, pk=None):
        # one Bin by pid, with the images for each species
        cache_key = create_cache_key(request, pk)
        cached_data = cache.get(cache_key)
        if cached_data:
            print("CACHE HIT")
            return Response(cached_data)

        options = self.get_options()
        try:
            bin_data = self.fetch_bin(options, pk)
            if not bin_data:
                return self.not_found(pk)
            images = self.fetch_images(bin_data, options)
        except Exception as err:
            return self.error_response(err)

        feature = self.build_feature(bin_data, options, self.get_datasets(), images)
        feature["properties"]["agreement"] = options["agreement"]
        feature["properties"]["score_thresholds"] = self.format_score_thresholds(options)

        cache.set(cache_key, feature, self.cache_timeout)
        return Response(feature)

    @action(detail=True, methods=["get"])
    def get_species_images(self, request, pk=None):
        # links to the images of one species in the Bin, same format as v1.
        # The species param can be the species ID or display name.
        species_name = request.query_params.get("species", None)
        species = TargetSpecies.objects.filter(
            Q(species_id=species_name) | Q(display_name=species_name)
        ).first()
        if not species_name or not species:
            return Response(
                {"statusCode": 400, "body": f"Unknown species: {species_name}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache_key = create_cache_key(request, pk)
        cached_data = cache.get(cache_key)
        if cached_data:
            print("CACHE HIT")
            return Response(cached_data)

        options = self.get_options()
        options = dict(
            options,
            species_ids=[species.species_id],
            score_thresholds={
                species.species_id: options["score_thresholds"].get(
                    species.species_id, float(species.autoclass_threshold)
                )
            },
        )
        try:
            bin_data = self.fetch_bin(options, pk)
            if not bin_data:
                return self.not_found(pk)
            images = self.fetch_images(bin_data, options).get(species.species_id, [])
        except Exception as err:
            return self.error_response(err)

        dataset = self.get_datasets().get(bin_data["datasetId"])
        dashboard_url = DEFAULT_DASHBOARD_URL
        if dataset:
            dashboard_url = dataset.dashboard_public_url or dataset.dashboard_base_url
        result = bin_data["species"][species.species_id]

        bin_images = {
            "bin": {
                "pid": bin_data["binPid"],
                "dataset_id": bin_data["datasetId"],
                "dataset_link": dashboard_url,
            },
            "species": species.display_name,
            "images": [
                f"{dashboard_url}/{bin_data['datasetId']}/{image_pid}.png"
                for image_pid in images[: self.images_limit]
            ],
            # number of different images the agreeing models found, image_count in
            # the detail view is the mean number of images per agreeing model
            "image_total": len(images),
            "agreement": options["agreement"],
            "models_agreed": result["modelsAgreed"],
            "models_run": bin_data["modelsRun"],
            "models_required": bin_data["modelsRequired"],
        }

        cache.set(cache_key, bin_images, self.cache_timeout)
        return Response(bin_images)
