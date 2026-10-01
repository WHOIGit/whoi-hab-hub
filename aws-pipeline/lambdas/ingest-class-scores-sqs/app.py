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


# Per-Bin summary index used by the HABhub API spatial grid.
# One document per Bin (_id = binPid). "speciesCounts" holds the number of images
# classified as each species by each model: {species: {modelId: count}}.
# "speciesScores" holds a histogram of those images' scores in 0.01 buckets so any
# score threshold can be applied at query time:
# {species: {modelId: [[bucket, count], ...]}}, bucket = floor(score * 100), 0-99.
# Both are stored in _source only (enabled: false) so dynamic species/model keys
# don't add fields to the index mapping.
# Keep in sync with habhub-dataserver ifcb_datasets/opensearch.py
SUMMARY_INDEX_NAME = "bin-species-summary"
SUMMARY_INDEX_BODY = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 1},
    "mappings": {
        "properties": {
            "binPid": {"type": "keyword"},
            "datasetId": {"type": "keyword"},
            "sampleTime": {"type": "date"},
            "dateUpdated": {"type": "date"},
            "point": {"type": "geo_point"},
            "mlAnalyzed": {"type": "float"},
            "modelIds": {"type": "keyword"},
            "speciesCounts": {"type": "object", "enabled": False},
            "speciesScores": {"type": "object", "enabled": False},
        }
    },
}

# Per-Bin, per-species score histograms, so the API only loads the species it needs.
# One document per Bin/species (_id = {binPid}_{species}).
# "modelScores" is the species' entry from the summary "speciesScores":
# {modelId: [[bucket, count], ...]}
# Keep in sync with habhub-dataserver ifcb_datasets/opensearch.py
SPECIES_SCORES_INDEX_NAME = "bin-species-scores"
SPECIES_SCORES_INDEX_BODY = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 1},
    "mappings": {
        "properties": {
            "binPid": {"type": "keyword"},
            "species": {"type": "keyword"},
            "datasetId": {"type": "keyword"},
            "sampleTime": {"type": "date"},
            "dateUpdated": {"type": "date"},
            "point": {"type": "geo_point"},
            "modelScores": {"type": "object", "enabled": False},
        }
    },
}

# Set one model's histogram in a species score document
SPECIES_UPDATE_SCRIPT = """
if (ctx._source.modelScores == null) {
    ctx._source.modelScores = new HashMap();
}
ctx._source.modelScores.put(params.modelId, params.histogram);
ctx._source.putAll(params.metadata);
"""

# Remove a model from species score documents it no longer found when a file is
# re-ingested, delete the document if no models are left
SPECIES_REMOVE_MODEL_SCRIPT = """
if (!ctx._source.modelScores.containsKey(params.modelId)) {
    ctx.op = 'noop';
} else {
    ctx._source.modelScores.remove(params.modelId);
    if (ctx._source.modelScores.isEmpty()) {
        ctx.op = 'delete';
    }
}
"""

# Merge one model's species counts/scores into the Bin summary document. Multiple models
# for the same Bin can be ingested concurrently, so this runs as a script update
# (with retry_on_conflict) instead of replacing the whole document.
# Any previous values for this model are removed first so re-ingesting a file is idempotent.
SUMMARY_UPDATE_SCRIPT = """
for (def field : params.speciesValues.entrySet()) {
    if (ctx._source[field.getKey()] == null) {
        ctx._source[field.getKey()] = new HashMap();
    }
    def speciesMap = ctx._source[field.getKey()];
    for (def modelValues : speciesMap.values()) {
        modelValues.remove(params.modelId);
    }
    for (def entry : field.getValue().entrySet()) {
        if (!speciesMap.containsKey(entry.getKey())) {
            speciesMap.put(entry.getKey(), new HashMap());
        }
        speciesMap.get(entry.getKey()).put(params.modelId, entry.getValue());
    }
    speciesMap.values().removeIf(modelValues -> modelValues.isEmpty());
}
ctx._source.putAll(params.metadata);
if (ctx._source.modelIds == null) {
    ctx._source.modelIds = new ArrayList();
}
if (!ctx._source.modelIds.contains(params.modelId)) {
    ctx._source.modelIds.add(params.modelId);
}
"""


def score_bucket(score):
    # 0.01 wide histogram bucket for a score. The small offset keeps float32 scores
    # like 0.7 (stored as 0.69999999) in the right bucket.
    # Keep in sync with habhub-dataserver backfill_bin_species_summary command
    return min(int(float(score) * 100 + 0.0001), 99)


def upsert_bin_summary(documents, metadata_obj, model_id, os_client):
    # count the images classified as each species by this model,
    # and the histogram of their scores
    counts = {}
    buckets = {}
    for document in documents:
        species = document["species"]
        counts[species] = counts.get(species, 0) + 1
        species_buckets = buckets.setdefault(species, {})
        bucket = score_bucket(document["score"])
        species_buckets[bucket] = species_buckets.get(bucket, 0) + 1

    scores = {
        species: sorted([bucket, count] for bucket, count in species_buckets.items())
        for species, species_buckets in buckets.items()
    }

    metadata = {
        "binPid": metadata_obj["binPid"],
        "datasetId": metadata_obj["datasetId"],
        "sampleTime": metadata_obj["sampleTime"],
        "point": metadata_obj["point"],
        "mlAnalyzed": metadata_obj["mlAnalyzed"],
        "dateUpdated": datetime.now().isoformat(),
    }

    # create indexes if they're missing, ignore error if another Lambda just created them
    for index_name, index_body in (
        (SUMMARY_INDEX_NAME, SUMMARY_INDEX_BODY),
        (SPECIES_SCORES_INDEX_NAME, SPECIES_SCORES_INDEX_BODY),
    ):
        if not os_client.indices.exists(index=index_name):
            os_client.indices.create(index=index_name, body=index_body, ignore=400)

    # check if this model has already been ingested for the Bin
    existing = os_client.get(
        index=SUMMARY_INDEX_NAME,
        id=metadata_obj["binPid"],
        _source_includes=["modelIds"],
        ignore=404,
    )
    is_reingest = model_id in existing.get("_source", {}).get("modelIds", [])

    response = os_client.update(
        index=SUMMARY_INDEX_NAME,
        id=metadata_obj["binPid"],
        body={
            "script": {
                "source": SUMMARY_UPDATE_SCRIPT,
                "lang": "painless",
                "params": {
                    "modelId": model_id,
                    "speciesValues": {
                        "speciesCounts": counts,
                        "speciesScores": scores,
                    },
                    "metadata": metadata,
                },
            },
            "upsert": metadata
            | {
                "modelIds": [model_id],
                "speciesCounts": {
                    species: {model_id: count} for species, count in counts.items()
                },
                "speciesScores": {
                    species: {model_id: histogram}
                    for species, histogram in scores.items()
                },
            },
        },
        retry_on_conflict=10,
    )
    print(response)

    upsert_species_scores(scores, metadata, model_id, is_reingest, os_client)
    return response


def upsert_species_scores(scores, metadata, model_id, is_reingest, os_client):
    # set this model's histogram in the score document for each species it found
    species_metadata = {
        key: metadata[key]
        for key in ("binPid", "datasetId", "sampleTime", "point", "dateUpdated")
    }
    operations = []
    for species, histogram in scores.items():
        operations.append(
            {
                "_op_type": "update",
                "_index": SPECIES_SCORES_INDEX_NAME,
                "_id": f"{metadata['binPid']}_{species}",
                "retry_on_conflict": 10,
                "script": {
                    "source": SPECIES_UPDATE_SCRIPT,
                    "lang": "painless",
                    "params": {
                        "modelId": model_id,
                        "histogram": histogram,
                        "metadata": species_metadata,
                    },
                },
                "upsert": species_metadata
                | {"species": species, "modelScores": {model_id: histogram}},
            }
        )
    response = helpers.bulk(os_client, operations, max_retries=3)
    print("Species scores upsert", response)

    if is_reingest:
        # remove this model from species it found before, but not in this file
        response = os_client.update_by_query(
            index=SPECIES_SCORES_INDEX_NAME,
            body={
                "query": {
                    "bool": {
                        "must": [{"term": {"binPid": metadata["binPid"]}}],
                        "must_not": [{"terms": {"species": list(scores)}}],
                    }
                },
                "script": {
                    "source": SPECIES_REMOVE_MODEL_SCRIPT,
                    "lang": "painless",
                    "params": {"modelId": model_id},
                },
            },
            conflicts="proceed",
        )
        print("Species scores re-ingest cleanup", response)


def process_message(event):
    print(event)
    body = json.loads(event["body"])
    lambda_resp = None
    # parse the S3 file received
    try:
        s3_Bucket_Name = body["Records"][0]["s3"]["bucket"]["name"]
        s3_File_Name = body["Records"][0]["s3"]["object"]["key"]
        print(s3_File_Name)
        # get the Bin pid
        file_name = Path(s3_File_Name).stem
        file_path = f"/tmp/{file_name}.h5"
        # download file to tmp directory
        result = s3_client.download_file(s3_Bucket_Name, s3_File_Name, file_path)

        bin_pid = file_name.replace("_class", "")
        print("Bin pid:", bin_pid)

        # get the model name from S3 key path in case missing from metadata
        try:
            model_id = s3_File_Name.split("/")[2]
        except:
            model_id = "unknown"
        print("Model id:", model_id)

    except Exception as err:
        print(err)
        lambda_resp = {"statusCode": 400, "body": json.dumps("Error reading S3")}

    # Get Dynamo metadata record
    """
    try:
        dynamodb = boto3.resource("dynamodb")
        table_name = "habhub-bins-metadata"
        table = dynamodb.Table(table_name)
        # get metadata item from database
        test_bin = "D20200309T180635_IFCB124"
        item = table.get_item(Key={"pid": "D20200309T180635_IFCB124"})
        print("Metadata", item)
        metadata = item.get("Item", None)
        print(metadata)
    except Exception as err:
        print(err)
        return None
    """

    # continue processing if error is null
    if not lambda_resp:
        # Get metadata from HABON IFCB dashboard
        test_bin = "D20200309T180635_IFCB124"
        dashboard_url = f"https://habon-ifcb.whoi.edu/api/bin/{bin_pid}"
        try:
            response = requests.get(dashboard_url)
            print(response)
            if response.status_code == 200:
                print(response.json())
                metadata = response.json()
                # check for Skip flag
                if not metadata["skip"]:
                    # parse ml_analyzed to just get the float
                    ml_analyzed = float(metadata["ml_analyzed"].split(" ")[0])
                    print("ml_analyzed", ml_analyzed)
                    point = [metadata["lng"], metadata["lat"]]
                    metadata_obj = {
                        "binPid": bin_pid,
                        "point": point,
                        "mlAnalyzed": ml_analyzed,
                        "datasetId": metadata["primary_dataset"],
                        "sampleTime": metadata["timestamp_iso"],
                        "dateCreated": datetime.now().isoformat(),
                    }
                    print("metadata_obj", metadata_obj)
                else:
                    print(f"Skip flag is true. Skip {bin_pid}")
                    lambda_resp = {
                        "statusCode": 200,
                        "body": json.dumps(f"Skip flag is true. Skip {bin_pid}"),
                    }
            else:
                print(f"No metadata available on HABON IFCB. Skip {bin_pid}")
                lambda_resp = {
                    "statusCode": 200,
                    "body": json.dumps(
                        f"No metadata available on HABON IFCB. Skip {bin_pid}"
                    ),
                }
        except Exception as err:
            print(err)
            lambda_resp = {
                "statusCode": 400,
                "body": json.dumps("Error connecting to Habon-IFCB"),
            }

    if not lambda_resp:
        # Connect to OS for indexing
        # host = "vpc-habhub-prod-3jxcbqq7ogktcoym3jnmjhgxsi.us-east-1.es.amazonaws.com"  # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
        host = "search-habhub-production-li4bxtldklbdlnyv6kuav3p4kq.us-east-1.es.amazonaws.com"
        region = "us-east-1"
        service = "es"
        credentials = boto3.Session().get_credentials()
        auth = AWSV4SignerAuth(credentials, region, service)
        # Create an index with non-default settings.
        index_name = "species-scores"
        # mapping dictionary that contains the settings and
        # _mapping schema for a new Elasticsearch index:
        # _id = binPid_imageNumber_modelName
        index_body = {
            "settings": {"number_of_shards": 2, "number_of_replicas": 1},
            "mappings": {
                "properties": {
                    "binPid": {"type": "keyword"},
                    "imageNumber": {"type": "keyword"},
                    "imagePid": {"type": "keyword"},
                    "score": {"type": "float"},
                    "modelId": {"type": "keyword"},
                    "species": {"type": "keyword"},
                    "sampleTime": {"type": "date"},
                    "dateCreated": {"type": "date"},
                    "datasetId": {"type": "keyword"},
                    "point": {"type": "geo_point"},
                    "mlAnalyzed": {"type": "float"},
                }
            },
        }

        try:
            os_client = OpenSearch(
                hosts=[{"host": host, "port": 443}],
                http_auth=auth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                pool_maxsize=20,
                timeout=20,
            )
            print("Connect to OS", os_client)
            info = os_client.info()
            print(info)

            # create index if it's missing
            if not os_client.indices.exists(index=index_name):
                print("No Index")
                # response = os_client.indices.delete(index=index_name, ignore_unavailable=True)
                response = os_client.indices.create(index_name, body=index_body)
                print("\nCreating index:")
                print(response)
            else:
                print("Index Exists")
                test_response = os_client.indices.get(index_name)
                print(test_response)

            # parse the H5 file and index results
            # read file into h5py
            f = h5py.File(file_path, "r")
            print(list(f.keys()))
            # get the data frames
            metadata = f["metadata"]
            scores = f["output_scores"]
            classes = f["class_labels"]
            rois = f["roi_numbers"]

            """
            try:
                model_id = metadata.attrs["model_id"]
            except Exception as err:
                print(err)
                print("model_id missing from metadata, set from S3 key")
            """

            documents = []
            # calculate the species with the max score
            for index, score in enumerate(scores):
                max_index = numpy.argmax(score)
                max_value = score[max_index]
                species = classes[max_index].decode("UTF-8")
                roi = rois[index]
                # print(score)

                score_obj = {}
                # print(species, max_value, roi)
                score_obj["species"] = species
                score_obj["score"] = max_value
                score_obj["imageNumber"] = roi
                score_obj["imagePid"] = f"{bin_pid}_{roi:05}"
                score_obj["modelId"] = model_id
                score_obj["osId"] = f"{bin_pid}_{roi:05}_{model_id}"
                document_obj = metadata_obj | score_obj
                documents.append(document_obj)

            # insert or update document into OpenSearch
            print("Start upsert ", len(documents))
            upsert_documents(documents, index_name, os_client)
            print("Bulk upsert ", len(documents))
            # update the per-Bin species counts summary
            upsert_bin_summary(documents, metadata_obj, model_id, os_client)
            print("Bin summary upsert ", bin_pid)

        except Exception as err:
            print(err)
            lambda_resp = {
                "statusCode": 400,
                "body": json.dumps("Error indexing documents"),
            }

    # clean up and return response
    # delete file from tmp dir
    os.remove(file_path)
    # delete file from S3
    response = s3_client.delete_object(Bucket=s3_Bucket_Name, Key=s3_File_Name)
    print("file deleted", s3_Bucket_Name, s3_File_Name)
    return {"statusCode": 200, "body": json.dumps(f"{bin_pid} successfully indexed")}
