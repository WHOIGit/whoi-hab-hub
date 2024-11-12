import environ
import hashlib
import json
import datetime
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from requests_aws4auth import AWS4Auth

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .mixins import ScoresFiltersMixin

env = environ.Env()

AWS_ACCESS_KEY_ID = env("DJANGO_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("DJANGO_AWS_SECRET_ACCESS_KEY")


# API view to return species scorer resutls from AWS Opensearch
class SpeciesScoresIndexViewSet(ScoresFiltersMixin, viewsets.ViewSet):
    def list(self, request):
        # Connect to OS for indexing
        host = "vpc-habhub-prod-3jxcbqq7ogktcoym3jnmjhgxsi.us-east-1.es.amazonaws.com"  # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
        region = "us-east-1"
        service = "es"
        awsauth = AWS4Auth(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, region, service)
        index_name = "species-scores"

        # build the query
        query = self.handle_query_param_filters()

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
            # search the DB
            response = os_client.search(body=query, index=index_name)
            print(response["hits"])
        except Exception as err:
            print(err)
            return Response(
                {
                    "statusCode": 400,
                    "body": "Error Connecting",
                }
            )

        return Response(response)
