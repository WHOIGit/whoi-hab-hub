# Per-Bin summary index used by the v2 spatial grid API.
# One document per Bin (_id = binPid). "speciesCounts" holds the number of images
# classified as each species by each model: {species: {modelId: count}}.
# It's stored in _source only (enabled: false) so dynamic species/model keys
# don't add fields to the index mapping.
# Written by the "ingest-class-scores-sqs" Lambda, keep the mapping in sync with
# aws-pipeline/lambdas/ingest-class-scores-sqs/app.py
SCORES_INDEX_NAME = "species-scores"
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
        }
    },
}


def create_summary_index(os_client):
    if not os_client.indices.exists(index=SUMMARY_INDEX_NAME):
        # ignore error if the index was just created by the ingest Lambda
        os_client.indices.create(
            index=SUMMARY_INDEX_NAME, body=SUMMARY_INDEX_BODY, ignore=400
        )
