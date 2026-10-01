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
# "h" holds the same histograms as doc values so the spatial grid can be aggregated
# in Opensearch: {species: {modelId: [bucket * 1000000 + count, ...]}}. Each
# h.{species}.{modelId} is its own field (not indexed, doc values only), so the
# mapping grows with the number of species/models and needs a higher field limit.
SUMMARY_INDEX_NAME = "bin-species-summary"
HISTOGRAM_BUCKET_FACTOR = 1000000
SUMMARY_FIELDS_LIMIT = 5000
SUMMARY_INDEX_BODY = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        "index.mapping.total_fields.limit": SUMMARY_FIELDS_LIMIT,
    },
    "mappings": {
        "dynamic_templates": [
            {
                "histograms": {
                    "path_match": "h.*",
                    "match_mapping_type": "long",
                    "mapping": {"type": "long", "index": False, "doc_values": True},
                }
            }
        ],
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
            "h": {"type": "object"},
        },
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
    # the field limit can't be set by put_mapping, update it on an existing index
    os_client.indices.put_settings(
        index=SUMMARY_INDEX_NAME,
        body={"index.mapping.total_fields.limit": SUMMARY_FIELDS_LIMIT},
    )
    create_index(os_client, SPECIES_SCORES_INDEX_NAME, SPECIES_SCORES_INDEX_BODY)


def build_histogram_fields(species_scores):
    # encode the summary "speciesScores" histograms as the "h" doc value fields
    # Keep in sync with the ingest Lambda
    return {
        species: {
            model: [bucket * HISTOGRAM_BUCKET_FACTOR + count for bucket, count in histogram]
            for model, histogram in model_scores.items()
        }
        for species, model_scores in species_scores.items()
    }


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


# Scripted metric to build the spatial grid in Opensearch from the summary index doc
# values, so only one result per grid square is returned instead of every Bin.
# For each Bin: snap the point to the grid, count each model's images above the
# species' score threshold from the "h" histograms, apply the model agreement rule,
# and calculate the cell concentration. For each grid square: the number of Bins,
# the number of models run, and each species' max/sum value and model agreement at
# the max value.
# Matches IfcbSpatialGridViewSet.get_bin_agreement(), Math.rint rounds half to even
# like Python round() and PostGIS ST_SnapToGrid().
# params:
#   gridLevel: grid square size in degrees
#   species: species IDs
#   minBuckets: {species: round(threshold * 100)}
#   agreement: "all", "majority" or "any"
#   models: optional list of model IDs to use, omitted for all models
#           (scripted metric params can't contain nulls)
GRID_INIT_SCRIPT = "state.squares = new HashMap();"
GRID_MAP_SCRIPT = """
if (doc['mlAnalyzed'].size() == 0 || doc['point'].size() == 0) {
    return;
}
// doc values are float32, round to the original mL value
double mlAnalyzed = Math.round(doc['mlAnalyzed'].value * 1000000.0) / 1000000.0;
if (mlAnalyzed == 0) {
    return;
}
String key = (long) Math.rint(doc['point'].lon / params.gridLevel) + '|'
    + (long) Math.rint(doc['point'].lat / params.gridLevel);
def square = state.squares.get(key);
if (square == null) {
    square = [
        'bins': 0,
        'singleModelBins': 0,
        'minModelsRun': Integer.MAX_VALUE,
        'maxModelsRun': 0,
        'species': new HashMap()
    ];
    state.squares.put(key, square);
}

List modelIds = new ArrayList();
for (def model : doc['modelIds']) {
    if (!params.containsKey('models') || params.models.contains(model)) {
        modelIds.add(model);
    }
}
int modelsRun = modelIds.size();
square.bins += 1;
if (modelsRun == 1) {
    square.singleModelBins += 1;
}
if (modelsRun < square.minModelsRun) {
    square.minModelsRun = modelsRun;
}
if (modelsRun > square.maxModelsRun) {
    square.maxModelsRun = modelsRun;
}

// number of models that need to find the species
int modelsRequired = 1;
if (params.agreement == 'all') {
    modelsRequired = modelsRun;
} else if (params.agreement == 'majority') {
    modelsRequired = modelsRun / 2 + 1;
}
if (modelsRequired < 1) {
    modelsRequired = 1;
}

for (def species : params.species) {
    int minBucket = params.minBuckets.get(species);
    int modelsAgreed = 0;
    long totalCount = 0;
    for (def model : modelIds) {
        String field = 'h.' + species + '.' + model;
        if (!doc.containsKey(field) || doc[field].size() == 0) {
            continue;
        }
        long count = 0;
        for (long value : doc[field]) {
            if (value / 1000000 >= minBucket) {
                count += value % 1000000;
            }
        }
        if (count > 0) {
            modelsAgreed += 1;
            totalCount += count;
        }
    }
    // use the mean cell concentration of the agreeing models
    long concentration = 0;
    if (modelsAgreed > 0 && modelsAgreed >= modelsRequired) {
        concentration = (long) Math.rint(((double) totalCount / modelsAgreed) / mlAnalyzed * 1000);
    }

    def result = square.species.get(species);
    if (result == null) {
        result = ['max': 0L, 'sum': 0L, 'modelsAgreed': 0, 'modelsRun': 0];
        square.species.put(species, result);
    }
    result.sum += concentration;
    // ties keep the Bin with the most agreeing models, then the most models run
    if (concentration > result.max || (concentration == result.max && concentration > 0
            && (modelsAgreed > result.modelsAgreed
                || (modelsAgreed == result.modelsAgreed && modelsRun > result.modelsRun)))) {
        result.max = concentration;
        result.modelsAgreed = modelsAgreed;
        result.modelsRun = modelsRun;
    }
}
"""
GRID_COMBINE_SCRIPT = "return state.squares;"
# the summary index has 1 shard, merge squares across shards if that changes
GRID_REDUCE_SCRIPT = """
def squares = new HashMap();
for (def shardSquares : states) {
    if (shardSquares == null) {
        continue;
    }
    for (def entry : shardSquares.entrySet()) {
        def square = squares.get(entry.getKey());
        def other = entry.getValue();
        if (square == null) {
            squares.put(entry.getKey(), other);
            continue;
        }
        square.bins += other.bins;
        square.singleModelBins += other.singleModelBins;
        if (other.minModelsRun < square.minModelsRun) {
            square.minModelsRun = other.minModelsRun;
        }
        if (other.maxModelsRun > square.maxModelsRun) {
            square.maxModelsRun = other.maxModelsRun;
        }
        for (def speciesEntry : other.species.entrySet()) {
            def result = square.species.get(speciesEntry.getKey());
            def otherResult = speciesEntry.getValue();
            result.sum += otherResult.sum;
            if (otherResult.max > result.max || (otherResult.max == result.max && otherResult.max > 0
                    && (otherResult.modelsAgreed > result.modelsAgreed
                        || (otherResult.modelsAgreed == result.modelsAgreed
                            && otherResult.modelsRun > result.modelsRun)))) {
                result.max = otherResult.max;
                result.modelsAgreed = otherResult.modelsAgreed;
                result.modelsRun = otherResult.modelsRun;
            }
        }
    }
}
return squares;
"""
