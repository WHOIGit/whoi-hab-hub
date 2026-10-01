# HABhub OpenSearch indexes

HABhub stores IFCB classifier results in three indexes on the `habhub-production`
OpenSearch domain:

| Index | One document per | Written by | Read by |
|---|---|---|---|
| `species-scores` | image (ROI) per model | `ingest-class-scores-sqs` Lambda | `/api/v2/ifcb-species-scores/`, `/api/v2/ifcb-fixed-metrics/` |
| `bin-species-summary` | Bin | `ingest-class-scores-sqs` Lambda, `backfill_bin_species_summary` and `backfill_summary_histograms` commands | `/api/v2/ifcb-spatial-grid/` (list aggregation, detail metadata), `build_bin_species_scores` command |
| `bin-species-scores` | Bin and species | `ingest-class-scores-sqs` Lambda, `backfill_bin_species_summary` and `build_bin_species_scores` commands | `/api/v2/ifcb-spatial-grid/{geohash}/` (detail) |

`species-scores` is the raw data (about 1.6 billion documents). `bin-species-summary`
is a per-Bin rollup of it (about 306,000 documents), so the spatial grid can be served
without aggregating millions of image documents on every request. Its `h` fields let
OpenSearch build the whole spatial grid in one aggregation. `bin-species-scores`
splits each summary's score histograms into one small document per species, so the
detail endpoint only loads the target species instead of all ~100 classes.

The examples below are real documents from production, Bin `D20251204T005155_IFCB125`.

## `species-scores`

Each IFCB image is classified by each ML model. The Lambda stores one document per
image per model, with the model's highest-scoring class as `species`.

### Mapping

Settings: 2 shards, 1 replica.

```json
{
  "properties": {
    "binPid":      { "type": "keyword" },
    "imageNumber": { "type": "keyword" },
    "imagePid":    { "type": "keyword" },
    "osId":        { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
    "species":     { "type": "keyword" },
    "score":       { "type": "float" },
    "modelId":     { "type": "keyword" },
    "datasetId":   { "type": "keyword" },
    "sampleTime":  { "type": "date" },
    "dateCreated": { "type": "date" },
    "point":       { "type": "geo_point" },
    "mlAnalyzed":  { "type": "float" }
  }
}
```

`osId` isn't in the Lambda's index definition, so OpenSearch mapped it automatically
as `text` with a `keyword` sub-field. Use `osId.keyword` for exact matches.

### Example document

`_id`: `D20251204T005155_IFCB125_00419_HABLAB_20230626_AKsup2`

```json
{
  "osId": "D20251204T005155_IFCB125_00419_HABLAB_20230626_AKsup2",
  "binPid": "D20251204T005155_IFCB125",
  "imageNumber": 419,
  "imagePid": "D20251204T005155_IFCB125_00419",
  "species": "Pseudo-nitzschia",
  "score": 0.97412109375,
  "modelId": "HABLAB_20230626_AKsup2",
  "datasetId": "harpswell",
  "sampleTime": "2025-12-04T00:51:55+00:00",
  "dateCreated": "2026-03-23T13:36:52.869897",
  "point": [-69.957882, 43.792114],
  "mlAnalyzed": 3.936
}
```

### Fields

| Field | Description |
|---|---|
| `_id` / `osId` | `{binPid}_{imageNumber:05}_{modelId}`, so re-ingesting a file overwrites its documents |
| `binPid` | IFCB Bin ID |
| `imageNumber` / `imagePid` | ROI number within the Bin, and `{binPid}_{imageNumber:05}` |
| `species` | Class with the highest score for this image from this model (any class, not only target species) |
| `score` | That class's score, 0–1 |
| `modelId` | Classifier model, taken from the S3 key path of the H5 file |
| `datasetId` | IFCB Dashboard dataset (`primary_dataset` from HABON IFCB) |
| `sampleTime` | Bin sample time, UTC |
| `dateCreated` | When the document was indexed |
| `point` | `[longitude, latitude]` of the Bin |
| `mlAnalyzed` | Volume analyzed in mL |

## `bin-species-summary`

One document per Bin (`_id` = `binPid`) holding the number of images each model
classified as each species, and a histogram of those images' scores.

### Mapping

Settings: 1 shard, 1 replica, `index.mapping.total_fields.limit: 5000`.
Defined in `habhub-dataserver/habhub/ifcb_datasets/opensearch.py`, with a copy in
`aws-pipeline/lambdas/ingest-class-scores-sqs/app.py`. Keep the two in sync. This
applies to `bin-species-scores` too.

```json
{
  "dynamic_templates": [
    {
      "histograms": {
        "path_match": "h.*",
        "match_mapping_type": "long",
        "mapping": { "type": "long", "index": false, "doc_values": true }
      }
    }
  ],
  "properties": {
    "binPid":        { "type": "keyword" },
    "datasetId":     { "type": "keyword" },
    "sampleTime":    { "type": "date" },
    "dateUpdated":   { "type": "date" },
    "point":         { "type": "geo_point" },
    "mlAnalyzed":    { "type": "float" },
    "modelIds":      { "type": "keyword" },
    "speciesCounts": { "type": "object", "enabled": false },
    "speciesScores": { "type": "object", "enabled": false },
    "h":             { "type": "object" }
  }
}
```

Every `h.{species}.{modelId}` is its own field, created by the `histograms` dynamic
template. It's stored as doc values only, not indexed for search. `match_mapping_type: long`
applies the template to the numeric values only, not to the `h.{species}` objects.
About 160–200 classes × the models run make well over the default limit of 1,000 fields,
so the limit is raised to 5,000. Watch the field count if many new classes or models
are added.

`speciesCounts` and `speciesScores` have `"enabled": false`. They're kept in `_source`
but not indexed, so their species and model keys don't add fields to the mapping. The
catch is that they can't be used in queries or aggregations, not even `exists`. Filter
on the other fields and read these from `_source`.

These fields make each document large, 20–33 KB for a recent Bin. OpenSearch loads the
whole `_source` even when `_source` filtering returns only a few fields, so don't
read them for many Bins per request. Use the `h` doc values in scripts and
aggregations, or `docvalue_fields` for the other fields.

### Example document

Trimmed from 106 species to 3. `detritus` is kept to show that every class is stored,
not only target species. Its histograms are shortened to their last few buckets.

```json
{
  "binPid": "D20251204T005155_IFCB125",
  "datasetId": "harpswell",
  "sampleTime": "2025-12-04T00:51:55+00:00",
  "point": [-69.957882, 43.792114],
  "mlAnalyzed": 3.936,
  "modelIds": [
    "HABLAB_20230209_GoM2",
    "HABLAB_20230209_GoM3",
    "HABLAB_20230626_AKsup2",
    "HABLAB_20240110_Tripos1",
    "HABLAB_20240110_Tripos2"
  ],
  "speciesCounts": {
    "Pseudo-nitzschia": {
      "HABLAB_20230626_AKsup2": 2,
      "HABLAB_20240110_Tripos1": 1,
      "HABLAB_20240110_Tripos2": 1
    },
    "Karenia": {
      "HABLAB_20230209_GoM3": 16,
      "HABLAB_20240110_Tripos2": 3
    },
    "detritus": {
      "HABLAB_20230209_GoM2": 295,
      "HABLAB_20230209_GoM3": 286,
      "HABLAB_20230626_AKsup2": 333,
      "HABLAB_20240110_Tripos1": 298,
      "HABLAB_20240110_Tripos2": 294
    }
  },
  "speciesScores": {
    "Pseudo-nitzschia": {
      "HABLAB_20230626_AKsup2": [[87, 1], [97, 1]],
      "HABLAB_20240110_Tripos1": [[89, 1]],
      "HABLAB_20240110_Tripos2": [[83, 1]]
    },
    "Karenia": {
      "HABLAB_20230209_GoM3": [[42, 1], [43, 1], [54, 1], [58, 1], [63, 1], [67, 1], [74, 2], [81, 1], [88, 1], [90, 1], [91, 1], [92, 1], [95, 1], [99, 2]],
      "HABLAB_20240110_Tripos2": [[39, 2], [45, 1]]
    },
    "detritus": {
      "HABLAB_20230209_GoM2": [[96, 13], [97, 14], [98, 16], [99, 148]],
      "...": "4 more models"
    }
  },
  "h": {
    "Pseudo-nitzschia": {
      "HABLAB_20230626_AKsup2": [87000001, 97000001],
      "HABLAB_20240110_Tripos1": [89000001],
      "HABLAB_20240110_Tripos2": [83000001]
    },
    "...": "same species and models as speciesScores"
  },
  "dateUpdated": "2026-09-30T18:43:26.023546"
}
```

### Fields

| Field | Description |
|---|---|
| `binPid` | IFCB Bin ID, also the document `_id` |
| `datasetId`, `sampleTime`, `point`, `mlAnalyzed` | Same as in `species-scores` |
| `modelIds` | Every model that has classified this Bin, including models that found none of a given species |
| `speciesCounts` | `{species: {modelId: count}}`: number of images each model classified as each species |
| `speciesScores` | `{species: {modelId: [[bucket, count], ...]}}`: score histogram of those images |
| `h` | `{species: {modelId: [bucket * 1000000 + count, ...]}}`: the same histograms as doc values, for aggregation scripts |
| `dateUpdated` | Last time the document was written |

About `speciesScores`:
- **Buckets:** each is 0.01 wide: `bucket = floor(score * 100)`, from 0 to 99, where 99 holds scores of 0.99–1.00. Only non-empty buckets are stored, in ascending order.
- **Totals:** a histogram's counts add up to the matching `speciesCounts` value.
- **Thresholds:** to count images scoring at or above a threshold `t`, sum the buckets that are ≥ `round(t * 100)`. Because the buckets are 0.01 wide, this is exact for any 2-decimal threshold, which is the precision of `TargetSpecies.autoclass_threshold`.
- **`h` encoding:** each value is `bucket * 1000000 + count`, so `value / 1000000` is the bucket and `value % 1000000` the count. Doc values are sorted, and because the bucket is the high part, they come back in bucket order. Counts are always under 1,000,000, since a Bin has far fewer images than that.
- **float32 rounding:** scores are float32, so 0.7 is stored as 0.69999999. The Lambda's `score_bucket()` and the backfill's histogram `offset` both add a small offset so a score like this lands in bucket 70, not 69.

### How it's written

- **Lambda:** `ingest-class-scores-sqs` processes one H5 file, meaning one Bin and one model. It merges that model's counts, histograms and `h` values into the Bin's document with a script update, using `retry_on_conflict` because several models' files for the same Bin can arrive at once. It removes that model's old values first, so re-ingesting a file is safe.
- **Backfill:** `python manage.py backfill_bin_species_summary --start_date=YYYY-MM-DD --end_date=YYYY-MM-DD [--chunk_hours=1] [--workers=2]` rebuilds documents from `species-scores`, replacing each one completely. It also writes their `bin-species-scores` documents. A Lambda update to the same Bin during a backfill can be overwritten, so re-run the last few days afterwards. Chunks that fail because the cluster is busy are retried up to 5 times.
- **Histogram fields only:** `python manage.py backfill_summary_histograms --start_date=YYYY-MM-DD --end_date=YYYY-MM-DD [--workers=2]` adds `h` to existing documents from their `speciesScores` as partial updates, without re-aggregating `species-scores`.
- **Bulk size:** AWS OpenSearch limits requests to 10 MB on smaller instances, and summary documents are large, so the commands cap bulk requests at 5 MB.
- **Adding a field:** add it to both mapping definitions. Then run `create_summary_index()` against the existing index **before** deploying a Lambda that writes the field. Both commands call it, and it creates or updates both summary indexes. Otherwise OpenSearch maps the new field's keys automatically.

## `bin-species-scores`

One document per Bin and species (`_id` = `{binPid}_{species}`). Its `modelScores` is
that species' entry from the summary document's `speciesScores`. There's a document
for every class a model found in the Bin, not only target species. A species no model
found has no document.

### Mapping

Settings: 1 shard, 1 replica.

```json
{
  "properties": {
    "binPid":      { "type": "keyword" },
    "species":     { "type": "keyword" },
    "datasetId":   { "type": "keyword" },
    "sampleTime":  { "type": "date" },
    "dateUpdated": { "type": "date" },
    "point":       { "type": "geo_point" },
    "modelScores": { "type": "object", "enabled": false }
  }
}
```

`modelScores` is in `_source` only, like the summary's `speciesCounts` and
`speciesScores`. Unlike the summary, each document is small, a few hundred bytes, so
loading it is cheap.

### Example document

The Pseudo-nitzschia document for the Bin above:

`_id`: `D20251204T005155_IFCB125_Pseudo-nitzschia`

```json
{
  "binPid": "D20251204T005155_IFCB125",
  "species": "Pseudo-nitzschia",
  "datasetId": "harpswell",
  "sampleTime": "2025-12-04T00:51:55+00:00",
  "dateUpdated": "2026-09-30T18:43:26.023546",
  "point": [-69.957882, 43.792114],
  "modelScores": {
    "HABLAB_20230626_AKsup2": [[87, 1], [97, 1]],
    "HABLAB_20240110_Tripos1": [[89, 1]],
    "HABLAB_20240110_Tripos2": [[83, 1]]
  }
}
```

### Fields

| Field | Description |
|---|---|
| `binPid`, `datasetId`, `sampleTime`, `point` | Copied from the Bin, so the same date, dataset and bounding box filters work on both summary indexes |
| `species` | The class |
| `modelScores` | `{modelId: [[bucket, count], ...]}`: score histogram of the images each model classified as this species. Same buckets as `speciesScores` |
| `dateUpdated` | Last time the document was written. The build command copies it from the summary document |

### How it's written

- **Lambda:** after updating the summary, it sets the model's histogram in the document for each species the model found, using a script update with `retry_on_conflict`. If the model had already been ingested for the Bin, it also removes the model from species it no longer finds, and deletes documents with no models left.
- **Build from the summary:** `python manage.py build_bin_species_scores --start_date=YYYY-MM-DD --end_date=YYYY-MM-DD [--workers=2]` creates the documents from existing `bin-species-summary` documents, without re-aggregating `species-scores`.
- **Summary backfill:** `backfill_bin_species_summary` writes these documents as well.
- **Full rebuild:** both commands replace documents but don't delete ones whose species is no longer in the summary. For a full rebuild, delete the index first. `create_summary_index()` recreates it.

## How `/api/v2/ifcb-spatial-grid/` uses the indexes

**List (the grid):** one `scripted_metric` aggregation on `bin-species-summary`, filtered
by date, dataset and bounding box. `GRID_MAP_SCRIPT` (in `ifcb_datasets/opensearch.py`)
runs once per Bin, using doc values only. It snaps `point` to the grid, applies the steps
below, and adds the result to its grid square. The response has one entry per square,
keyed `"{lng index}|{lat index}"`, where the grid point is `index * grid_level`. Django
only adds geohashes and builds the GeoJSON, so the response size depends on the number
of squares, not the length of the date range. A 2-year range takes about 2 seconds in
OpenSearch.

**Detail (one square):** two paged queries at the same time, filtered to the square's
bounding box:

1. **`bin-species-summary`:** every Bin in the square, so Bins without a species still count as 0. It reads `binPid`, `sampleTime`, `point`, `mlAnalyzed` and `modelIds` through `docvalue_fields` with `_source: false`.
2. **`bin-species-scores`:** only the target species' documents. The script field `MODEL_COUNTS_SCRIPT` applies each species' threshold inside OpenSearch and returns only each model's image count.

Both use `filter_path` to keep the responses small. The detail view applies the same
steps in Python, in `IfcbSpatialGridViewSet.get_bin_agreement()`. Keep it and
`GRID_MAP_SCRIPT` in sync.

For each Bin and target species:

1. **Count the images at or above the threshold** for each model. The threshold is the species' `TargetSpecies.autoclass_threshold`, or `score_gte` if the request passes one.
2. **Count the agreeing models.** A model agrees if its count is above 0.
3. **Work out how many models must agree.** It depends on the `agreement` param and N, the number of models that processed the Bin (`len(modelIds)`, after any `model_id` filter):

   | `agreement` | Models required | N = 1 | N = 4 | N = 5 |
   |---|---|---|---|---|
   | `all` | N | 1 | 4 | 5 |
   | `majority` (default) | more than half: ⌊N/2⌋ + 1 | 1 | 3 | 3 |
   | `any` | 1 | 1 | 1 | 1 |

   A Bin only one model processed counts in every mode if that model found the species.
4. **Calculate the concentration.** If enough models agree: `cell concentration = mean(agreeing counts) / mlAnalyzed * 1000` cells/L. Otherwise the value is 0.

Worked example, using the Bin above. 5 models ran, so `all` needs 5, `majority` needs 3
and `any` needs 1:

| Species | Threshold | Count per model at or above threshold | Agreeing | `all` | `majority` | `any` |
|---|---|---|---|---|---|---|
| Pseudo-nitzschia | 0.00 | AKsup2 2, Tripos1 1, Tripos2 1 | 3 | 0 | (4 / 3) / 3.936 × 1000 = **339** | **339** |
| Pseudo-nitzschia | 0.85 | AKsup2 2 (buckets 87, 97), Tripos1 1 (89), Tripos2 0 (83) | 2 | 0 | 0 | (3 / 2) / 3.936 × 1000 = **381** |
| Karenia | 0.00 | GoM3 16, Tripos2 3 | 2 | 0 | 0 | (19 / 2) / 3.936 × 1000 = **2,414** |

Values are cells/L. The concentration is always the mean of the agreeing models' counts,
so `any` doesn't average in models that found nothing.

`geo_point` and `float` doc values are encoded, so `point` has about 1e-7° precision
loss. `mlAnalyzed` comes back as float32 (3.473 → 3.4730000495910645), and both the
script and the detail view round it to 6 decimal places to get the original value back.
Rounding to the grid and of concentrations is half-even in both: `Math.rint` in Painless,
`round()` in Python.

Grid squares group Bins by snapping `point` to `grid_level` degrees, matching PostGIS
`ST_SnapToGrid()`. Each square's ID is the precision-5 geohash of its snapped point,
the same IDs as `/api/v1/ifcb-spatial-grid/`.
