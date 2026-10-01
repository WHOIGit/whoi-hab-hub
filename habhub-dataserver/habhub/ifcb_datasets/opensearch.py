# Opensearch indexes used by the v2 spatial grid API.
# Written by the "ingest-class-scores-sqs" Lambda, keep the mappings in sync with
# aws-pipeline/lambdas/ingest-class-scores-sqs/app.py
# See opensearch/INDEX_SCHEMAS.md for examples.
SCORES_INDEX_NAME = "species-scores"

# Per-Bin summary index. One document per Bin (_id = binPid).
# "speciesCounts" holds the number of images classified as each species by each
# model: {species: {modelId: count}}.
# "speciesScores" holds a histogram of those images' scores in 0.01 buckets:
# {species: {modelId: [[bucket, count], ...]}}, bucket = floor(score * 100), 0-99.
# Both are stored in _source only (enabled: false) so dynamic species/model keys
# don't add fields to the index mapping.
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

# Per-Bin, per-species score histograms. One small document per Bin/species
# (_id = {binPid}_{species}) so the API only loads the species it needs, instead of
# every species' histograms in the summary document.
# "modelScores" is the species' entry from the summary "speciesScores":
# {modelId: [[bucket, count], ...]}
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

# script field to count each model's images with a score >= the species' threshold,
# so only the counts are returned instead of the histograms.
# params.minBuckets: {species: round(threshold * 100)}
MODEL_COUNTS_SCRIPT = """
def counts = new HashMap();
int minBucket = params.minBuckets.get(doc['species'].value);
for (def entry : params._source.modelScores.entrySet()) {
    int count = 0;
    for (def bucket : entry.getValue()) {
        if (bucket[0] >= minBucket) {
            count += bucket[1];
        }
    }
    if (count > 0) {
        counts.put(entry.getKey(), count);
    }
}
return counts;
"""


def create_index(os_client, index_name, index_body):
    if not os_client.indices.exists(index=index_name):
        # ignore error if the index was just created by the ingest Lambda
        os_client.indices.create(index=index_name, body=index_body, ignore=400)
    # add any fields missing from an existing index. Needs to run before the
    # ingest Lambda writes a new field, or its dynamic keys would be mapped
    os_client.indices.put_mapping(index=index_name, body=index_body["mappings"])


def create_summary_index(os_client):
    create_index(os_client, SUMMARY_INDEX_NAME, SUMMARY_INDEX_BODY)
    create_index(os_client, SPECIES_SCORES_INDEX_NAME, SPECIES_SCORES_INDEX_BODY)


def build_species_score_documents(summary_document):
    # split a Bin summary document into one document per species
    return [
        {
            "binPid": summary_document["binPid"],
            "species": species,
            "datasetId": summary_document["datasetId"],
            "sampleTime": summary_document["sampleTime"],
            "dateUpdated": summary_document["dateUpdated"],
            "point": summary_document["point"],
            "modelScores": model_scores,
        }
        for species, model_scores in summary_document.get("speciesScores", {}).items()
    ]


def species_score_operations(summary_documents):
    # bulk index operations for the species score documents of each Bin
    return (
        {
            "_op_type": "index",
            "_index": SPECIES_SCORES_INDEX_NAME,
            "_id": f"{document['binPid']}_{document['species']}",
            "_source": document,
        }
        for summary_document in summary_documents
        for document in build_species_score_documents(summary_document)
    )
