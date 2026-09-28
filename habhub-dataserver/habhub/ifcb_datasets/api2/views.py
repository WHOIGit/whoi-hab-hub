import datetime
import environ
import urllib.parse
from collections import OrderedDict
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth, helpers
from requests_aws4auth import AWS4Auth

from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status, viewsets

# from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework_gis.fields import GeometryField
from .mixins import ScoresFiltersMixin
from ..models import Dataset
from ..api.cache_utils import create_cache_key
from ..opensearch import SUMMARY_INDEX_NAME
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


# API view to return spatial grid of species cell concentrations from AWS Opensearch.
# Matches the response format of the v1 "ifcb-spatial-grid" endpoint, but a species
# is only counted as present in a Bin if at least `min_models` ML models agree.
# Uses the per-Bin "bin-species-summary" index (see ifcb_datasets/opensearch.py)
# instead of aggregating the image level "species-scores" index on every request.
class IfcbSpatialGridViewSet(ScoresFiltersMixin, viewsets.ViewSet):
    default_grid_level = 0.5
    default_min_models = 3
    # number of Bin documents to return per page, max allowed by Opensearch
    bins_page_size = 10000
    cache_timeout = 60 * 60

    def get_options(self):
        # parse the query params shared by the list and detail views
        query_params = self.request.query_params

        try:
            grid_level = float(query_params.get("grid_level", self.default_grid_level))
        except ValueError:
            grid_level = self.default_grid_level

        if grid_level <= 0:
            grid_level = self.default_grid_level

        try:
            min_models = int(query_params.get("min_models", self.default_min_models))
        except ValueError:
            min_models = self.default_min_models

        species_param = query_params.get("species", None)
        species_list = list(TargetSpecies.objects.values_list("species_id", "display_name"))
        if species_param:
            requested_species = species_param.split(",")
            species_list = [s for s in species_list if s[0] in requested_species]

        model_param = query_params.get("model_id", None)

        metric = Metric.objects.filter(metric_id="cell_concentration").first()

        return {
            "grid_level": grid_level,
            "min_models": min_models,
            "species_ids": [species_id for species_id, _ in species_list],
            "species_display": dict(species_list),
            "model_list": model_param.split(",") if model_param else None,
            "metric_name": metric.name if metric else "Cell Concentration",
            "metric_units": metric.units if metric else "cells/L",
        }

    def fetch_bins(self, options, source_fields, sort, extra_filters=None):
        # return the summary documents for all Bins matching the query params
        query = self.handle_query_param_filters()
        # species/model/score are image level filters that don't exist in the summary
        # index. Every Bin in the date range is returned so Bins without the species
        # still count as 0, matching the v1 endpoint.
        must = [
            clause
            for clause in query["query"]["bool"]["must"]
            if not {"species", "modelId"} & clause.get("terms", {}).keys()
            and "score" not in clause.get("range", {})
        ]
        query["query"]["bool"]["must"] = must + (extra_filters or [])
        query["track_total_hits"] = False
        query["size"] = self.bins_page_size
        query["sort"] = sort
        # only return the species counts needed
        query["_source"] = source_fields + [
            f"speciesCounts.{species}" for species in options["species_ids"]
        ]

        os_client = connect_opensearch()
        bins = []
        # use search_after to page through all Bins
        while True:
            response = os_client.search(
                body=query, index=SUMMARY_INDEX_NAME, request_timeout=60
            )
            hits = response["hits"]["hits"]
            bins.extend(hit["_source"] for hit in hits)

            if len(hits) < self.bins_page_size:
                break
            query["search_after"] = hits[-1]["sort"]

        # skip Bins that can't be placed on the grid or have no volume
        return [
            bin_data
            for bin_data in bins
            if bin_data.get("mlAnalyzed") and bin_data.get("point")
        ]

    def get_bin_concentrations(self, bin_data, options):
        # return the cell concentration for each species in the Bin that enough models agree on
        concentrations = {}
        species_counts = bin_data.get("speciesCounts", {})
        for species in options["species_ids"]:
            model_counts = species_counts.get(species, {})
            if options["model_list"]:
                model_counts = {
                    model: count
                    for model, count in model_counts.items()
                    if model in options["model_list"]
                }
            # species is only present if enough models agree
            if len(model_counts) < options["min_models"]:
                continue
            # use the mean cell concentration of the agreeing models
            mean_count = sum(model_counts.values()) / len(model_counts)
            concentrations[species] = round(mean_count / bin_data["mlAnalyzed"] * 1000)

        return concentrations

    def get_grid_point(self, bin_data, grid_level):
        lng, lat = bin_data["point"]
        return snap_to_grid(lng, grid_level), snap_to_grid(lat, grid_level)

    def error_response(self, err):
        print(err)
        return Response(
            {
                "statusCode": 400,
                "body": "Error Running Query",
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    def list(self, request):
        cache_key = create_cache_key(request)
        cached_data = cache.get(cache_key)
        if cached_data:
            print("CACHE HIT")
            return Response(cached_data)

        options = self.get_options()
        try:
            bins = self.fetch_bins(
                options, ["point", "mlAnalyzed"], [{"binPid": "asc"}]
            )
        except Exception as err:
            return self.error_response(err)

        # group Bins into grid squares, calculate cell concentration for each species
        grid_squares = {}
        for bin_data in bins:
            square = grid_squares.setdefault(
                self.get_grid_point(bin_data, options["grid_level"]),
                {
                    "bin_count": 0,
                    "values": {species: [] for species in options["species_ids"]},
                },
            )
            square["bin_count"] += 1

            for species, value in self.get_bin_concentrations(bin_data, options).items():
                square["values"][species].append(value)

        # build the GeoJSON response
        geo_field = GeometryField()
        features = []
        for (grid_lng, grid_lat), square in sorted(grid_squares.items()):
            max_mean_values = []
            for species in options["species_ids"]:
                values = square["values"][species]
                max_mean_values.append(
                    {
                        "species": species,
                        "data": [
                            {
                                "metric_id": "cell_concentration",
                                "metric_name": options["metric_name"],
                                "max_value": max(values, default=0),
                                # Bins without the species count as 0
                                "mean_value": sum(values) / square["bin_count"],
                                "units": options["metric_units"],
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
            feature["properties"] = OrderedDict(max_mean_values=max_mean_values)
            features.append(feature)

        geojson = OrderedDict()
        # must be "FeatureCollection" according to GeoJSON spec
        geojson["type"] = "FeatureCollection"
        geojson["metadata"] = OrderedDict()
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
            bins = self.fetch_bins(
                options,
                ["binPid", "sampleTime", "point", "mlAnalyzed"],
                [{"sampleTime": "asc"}, {"binPid": "asc"}],
                extra_filters=[bbox_filter],
            )
        except Exception as err:
            return self.error_response(err)

        bins = [
            bin_data
            for bin_data in bins
            if self.get_grid_point(bin_data, grid_level) == (grid_lng, grid_lat)
        ]
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
            concentrations = self.get_bin_concentrations(bin_data, options)

            for species_item in timeseries_data:
                species_item["data"].append(
                    {
                        "sample_time": date_str,
                        "bin_pid": bin_data["binPid"],
                        "metrics": [
                            {
                                "metric_id": "cell_concentration",
                                "metric_name": options["metric_name"],
                                # Bins without the species are 0
                                "value": concentrations.get(
                                    species_item["species"], 0
                                ),
                                "units": options["metric_units"],
                            }
                        ],
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
        geojson["properties"] = OrderedDict(timeseries_data=timeseries_data)

        cache.set(cache_key, geojson, self.cache_timeout)
        return Response(geojson)
