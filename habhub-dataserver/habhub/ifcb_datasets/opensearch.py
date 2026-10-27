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
# "i" holds each model's images of the target species as doc values, so the model
# agreement can be checked image by image: {species: {modelId: [imageNumber * 100 + bucket, ...]}}
# Only TargetSpecies have "i" fields, the ingest Lambda gets them from the HABhub API.
# Only images with a score >= IMAGE_MIN_SCORE are stored, to keep the fields small for
# common species, so the API can't apply a lower score threshold.
SUMMARY_INDEX_NAME = "bin-species-summary"
HISTOGRAM_BUCKET_FACTOR = 1000000
IMAGE_BUCKET_FACTOR = 100
# minimum score of the images stored in the "i" fields, and its score bucket
# Keep in sync with the ingest Lambda
IMAGE_MIN_SCORE = 0.5
IMAGE_MIN_BUCKET = round(IMAGE_MIN_SCORE * 100)
SUMMARY_FIELDS_LIMIT = 10000
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
            },
            {
                "images": {
                    "path_match": "i.*",
                    "match_mapping_type": "long",
                    "mapping": {"type": "long", "index": False, "doc_values": True},
                }
            },
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
            "i": {"type": "object"},
        },
    },
}

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


def score_bucket(score):
    # 0.01 wide score bucket. The small offset keeps float32 scores like 0.7
    # (stored as 0.69999999) in the right bucket.
    # Keep in sync with score_bucket() in the ingest Lambda
    return min(int(float(score) * 100 + 0.0001), 99)


def build_image_fields(species_images):
    # encode {species: {modelId: [(imageNumber, bucket), ...]}} as the "i" doc value fields
    # Keep in sync with the ingest Lambda
    return {
        species: {
            model: sorted(image * IMAGE_BUCKET_FACTOR + bucket for image, bucket in images)
            for model, images in model_images.items()
        }
        for species, model_images in species_images.items()
    }


# Painless function to calculate a Bin's species results from the summary index doc
# values. The model agreement is checked image by image from the "i" fields: an image
# counts for a species if enough of the models run on the Bin classified it as that
# species with a score >= the species' threshold, set by params.agreement:
#   any:      at least one model
#   majority: more than half of the models
#   strict:   more than 80% of the models
# A single model run on a Bin counts for all three. The cell concentration is the
# number of images that count / mlAnalyzed * 1000.
# Shared by the grid aggregation (list views) and the Bin results script field
# (detail views) so all use the same rule. Math.rint rounds half to even like
# Python round() and PostGIS ST_SnapToGrid().
# Returns null for Bins without a point or volume, otherwise
#   ['modelsRun': int, 'modelsRequired': int,
#    'species': {species: ['value': long, 'imageCount': long, 'modelsAgreed': int,
#                          'images': [[imageNumber, votes, maxBucket], ...] (only if params.includeImages)]}]
# "modelsRequired" is the number of models that need to find an image, "modelsAgreed"
# the number of models that found any image of the species above its threshold.
# params:
#   species: species IDs
#   minBuckets: {species: round(threshold * 100)}
#   agreement: "any", "majority" or "strict"
#   models: optional list of model IDs to use, omitted for all models
#           (script params can't contain nulls)
#   includeImages: optional, true to return the images that count
BIN_RESULT_FUNCTION = """
Map binResult(Map doc, Map params) {
    if (doc['mlAnalyzed'].size() == 0 || doc['point'].size() == 0) {
        return null;
    }
    // doc values are float32, round to the original mL value
    double mlAnalyzed = Math.round(doc['mlAnalyzed'].value * 1000000.0) / 1000000.0;
    if (mlAnalyzed == 0) {
        return null;
    }

    List modelIds = new ArrayList();
    for (def model : doc['modelIds']) {
        if (!params.containsKey('models') || params.models.contains(model)) {
            modelIds.add(model);
        }
    }
    int modelsRun = modelIds.size();

    // number of models that need to find an image for it to count
    int modelsRequired = 1;
    if (params.agreement == 'strict') {
        // more than 80%
        modelsRequired = modelsRun * 4 / 5 + 1;
    } else if (params.agreement == 'majority') {
        // more than half
        modelsRequired = modelsRun / 2 + 1;
    }
    boolean includeImages = params.containsKey('includeImages') && params.includeImages;

    Map speciesResults = new HashMap();
    for (def species : params.species) {
        int minBucket = params.minBuckets.get(species);
        // votes and highest score bucket for each image number
        Map votes = new HashMap();
        Map maxBuckets = new HashMap();
        int modelsAgreed = 0;
        for (def model : modelIds) {
            String field = 'i.' + species + '.' + model;
            if (!doc.containsKey(field) || doc[field].size() == 0) {
                continue;
            }
            boolean found = false;
            for (long value : doc[field]) {
                long bucket = value % 100;
                if (bucket < minBucket) {
                    continue;
                }
                long image = value / 100;
                votes.put(image, votes.getOrDefault(image, 0) + 1);
                if (bucket > maxBuckets.getOrDefault(image, -1L)) {
                    maxBuckets.put(image, bucket);
                }
                found = true;
            }
            if (found) {
                modelsAgreed += 1;
            }
        }

        long imageCount = 0;
        List images = new ArrayList();
        for (def entry : votes.entrySet()) {
            if (entry.getValue() >= modelsRequired) {
                imageCount += 1;
                if (includeImages) {
                    images.add([entry.getKey(), entry.getValue(), maxBuckets.get(entry.getKey())]);
                }
            }
        }
        long concentration = (long) Math.rint(imageCount / mlAnalyzed * 1000);
        Map speciesResult = ['value': concentration, 'imageCount': imageCount, 'modelsAgreed': modelsAgreed];
        if (includeImages) {
            speciesResult.put('images', images);
        }
        speciesResults.put(species, speciesResult);
    }
    return ['modelsRun': modelsRun, 'modelsRequired': modelsRequired, 'species': speciesResults];
}
"""

# script field returning binResult() for each Bin, used by the detail view
BIN_RESULT_SCRIPT = BIN_RESULT_FUNCTION + "return binResult(doc, params);"

# Scripted metric to build the spatial grid in Opensearch from the summary index doc
# values, so only one result per grid square is returned instead of every Bin.
# For each Bin: snap the point to the grid and calculate binResult(). For each grid
# square: the number of Bins, the number of models run, and each species' max/sum
# value and model agreement at the max value.
# params: binResult() params, and
#   gridLevel: grid square size in degrees
GRID_INIT_SCRIPT = "state.squares = new HashMap();"
GRID_MAP_SCRIPT = BIN_RESULT_FUNCTION + """
def bin = binResult(doc, params);
if (bin == null) {
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

int modelsRun = bin.modelsRun;
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

for (def entry : bin.species.entrySet()) {
    long concentration = entry.getValue().value;
    int modelsAgreed = entry.getValue().modelsAgreed;
    def result = square.species.get(entry.getKey());
    if (result == null) {
        result = ['max': 0L, 'sum': 0L, 'modelsAgreed': 0, 'modelsRun': 0];
        square.species.put(entry.getKey(), result);
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
