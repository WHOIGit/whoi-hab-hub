import environ
import hashlib
import json
import datetime
import boto3
import urllib.parse
from collections import OrderedDict
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth, helpers
from requests_aws4auth import AWS4Auth

from rest_framework import viewsets, status
from rest_framework.reverse import reverse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_gis.fields import GeometryField
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .mixins import ScoresFiltersMixin
from ..models import Dataset

env = environ.Env()

AWS_ACCESS_KEY_ID = env("DJANGO_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("DJANGO_AWS_SECRET_ACCESS_KEY")


def connect_opensearch():
    # Connect to OS for indexing
    host = "vpc-habhub-prod-3jxcbqq7ogktcoym3jnmjhgxsi.us-east-1.es.amazonaws.com"  # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
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
        print(
            f"Welcome to {info['version']['distribution']} {info['version']['number']}!"
        )

    except Exception as err:
        print(err)
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
        link = reverse("api_v2:ifcb-species-scores-list", request=request)
        print("link", link)
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
            print(err)
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

        if not dataset_id or not species:
            return Response(
                {
                    "statusCode": 400,
                    "body": "Dataset ID required",
                }
            )

        species_list = species.split(",")

        # build the query
        query = self.handle_query_param_filters()
        # add aggregation
        agg = {
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
                }
            )

        # get the Dataset
        dataset = Dataset.objects.get(dashboard_id_name=dataset_id)
        print(dataset)

        # parse OpenSearch response
        timeseries_data = []
        for species in species_list:
            species_item = {
                "species": species,
                "species_display": species.replace("_", " "),
            }
            timeseries_data.append(species_item)

            data = []
            for item in response["aggregations"]["bin-agg"]["buckets"]:
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
