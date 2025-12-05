import json
import boto3
import h5py
import numpy
import requests
import os
from datetime import datetime
from pathlib import Path
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth, helpers

s3_client = boto3.client("s3")

BLACKLIST = [
    "nanoplankton_mix",
    "detritus",
    "detritus_transparent",
    "camera_spot",
    "bead",
    "bad",
    "fecal_pellet",
    "fiber",
    "fiber_TAG_external_detritus",
    "flagellate",
    "mix",
    "mix_elongated",
    "nanoplankton_mix",
    "pennate",
]


def lambda_handler(event, context):
    if event:
        batch_item_failures = []
        sqs_batch_response = {}

        for record in event["Records"]:
            try:
                # process message
                process_message(record)
            except Exception as e:
                batch_item_failures.append({"itemIdentifier": record["messageId"]})

        sqs_batch_response["batchItemFailures"] = batch_item_failures
        return sqs_batch_response


def upsert_documents(documents, index_name, os_client):
    operations = []
    for document in documents:
        # print(document)
        doc_id = document["osId"]
        operations.append(
            {
                "_op_type": "update",
                "_index": index_name,
                "_id": doc_id,
                "doc": document,
                "doc_as_upsert": True,
            }
        )
    response = helpers.bulk(os_client, operations, index=index_name, max_retries=3)
    print(response)
    return response


def process_message(message):
    print(message)

    return {"statusCode": 200, "body": json.dumps(f"successfully indexed")}
