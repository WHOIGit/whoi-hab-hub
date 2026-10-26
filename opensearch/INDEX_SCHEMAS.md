# HABhub OpenSearch indexes

HABhub stores IFCB classifier results in two indexes on the `habhub-production`
OpenSearch domain:

| Index | One document per | Written by | Read by |
|---|---|---|---|
| `species-scores` | image (ROI) per model | `ingest-class-scores-sqs` Lambda | `/api/v2/ifcb-species-scores/`, `/api/v2/ifcb-fixed-metrics/`, `backfill_bin_species_summary` and `backfill_summary_images` commands |
| `bin-species-summary` | Bin | `ingest-class-scores-sqs` Lambda, `backfill_bin_species_summary`, `backfill_summary_histograms` and `backfill_summary_images` commands | `/api/v2/ifcb-spatial-grid/`, `/api/v2/ifcb-bins/`, `/api/v2/ifcb-bin-locations/` |

`species-scores` is the raw data (about 1.6 billion documents). `bin-species-summary`
is a per-Bin rollup of it (about 306,000 documents), so the spatial grid can be served
without aggregating millions of image documents on every request. Its `i` fields hold
each model's images of the target species, so OpenSearch can check model agreement image
by image and build the whole spatial grid in one aggregation.

An earlier `bin-species-scores` index (one document per Bin and species) was replaced
by the `h` fields in October 2026 and is no longer written or read.

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

Settings: 1 shard, 1 replica, `index.mapping.total_fields.limit: 10000`.
Defined in `habhub-dataserver/habhub/ifcb_datasets/opensearch.py`, with a copy in
`aws-pipeline/lambdas/ingest-class-scores-sqs/app.py`. Keep the two in sync.

```json
{
  "dynamic_templates": [
    {
      "histograms": {
        "path_match": "h.*",
        "match_mapping_type": "long",
        "mapping": { "type": "long", "index": false, "doc_values": true }
      }
    },
    {
      "images": {
        "path_match": "i.*",
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
    "h":             { "type": "object" },
    "i":             { "type": "object" }
  }
}
```

Every `h.{species}.{modelId}` and `i.{species}.{modelId}` is its own field, created by the
`histograms` and `images` dynamic templates. It's stored as doc values only, not indexed for search. `match_mapping_type: long`
applies the template to the numeric values only, not to the `h.{species}` objects.
About 220 classes × the models run make well over the default limit of 1,000 fields
(2,874 `h` fields in October 2026), so the limit is raised to 10,000. Each new model can
add about 220 fields. If the limit is reached, Lambda updates that add new fields fail,
so watch the field count as classes and models are added.

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
  "i": {
    "Pseudo-nitzschia": {
      "HABLAB_20230626_AKsup2": [41997, 104387],
      "HABLAB_20240110_Tripos1": [104389],
      "HABLAB_20240110_Tripos2": [104383]
    },
    "...": "target species only"
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
| `h` | `{species: {modelId: [bucket * 1000000 + count, ...]}}`: the same histograms as doc values. No longer read by the API |
| `i` | `{species: {modelId: [imageNumber * 100 + bucket, ...]}}`: each image the model classified as the species, with its score bucket, as doc values. Target species only. Used for the per-image model agreement |
| `dateUpdated` | Last time the document was written |

About `speciesScores`:
- **Buckets:** each is 0.01 wide: `bucket = floor(score * 100)`, from 0 to 99, where 99 holds scores of 0.99–1.00. Only non-empty buckets are stored, in ascending order.
- **Totals:** a histogram's counts add up to the matching `speciesCounts` value.
- **Thresholds:** to count images scoring at or above a threshold `t`, sum the buckets that are ≥ `round(t * 100)`. Because the buckets are 0.01 wide, this is exact for any 2-decimal threshold, which is the precision of `TargetSpecies.autoclass_threshold`.
- **`h` encoding:** each value is `bucket * 1000000 + count`, so `value / 1000000` is the bucket and `value % 1000000` the count. Doc values are sorted, and because the bucket is the high part, they come back in bucket order. Counts are always under 1,000,000, since a Bin has far fewer images than that.
- **`i` encoding:** each value is `imageNumber * 100 + bucket`, so `value / 100` is the image (ROI) number and `value % 100` the score bucket. The `i` values in the example above are illustrative: image 419 at 0.97 is `41997`.
- **float32 rounding:** scores are float32, so 0.7 is stored as 0.69999999. The Lambda's `score_bucket()` and the backfill's histogram `offset` both add a small offset so a score like this lands in bucket 70, not 69.

### How it's written

- **Lambda:** `ingest-class-scores-sqs` processes one H5 file, meaning one Bin and one model. It merges that model's counts, histograms, `h` and `i` values into the Bin's document with a script update, using `retry_on_conflict` because several models' files for the same Bin can arrive at once. It removes that model's old values first, so re-ingesting a file is safe.
- **Backfill:** `python manage.py backfill_bin_species_summary --start_date=YYYY-MM-DD --end_date=YYYY-MM-DD [--chunk_hours=1] [--workers=2]` rebuilds documents from `species-scores`, replacing each one completely. A Lambda update to the same Bin during a backfill can be overwritten, so re-run the last few days afterwards. Chunks that fail because the cluster is busy are retried up to 5 times.
- **Target species for `i`:** the Lambda gets the list from `{HABHUB_API_URL}/api/v1/core/target-species/` (the `id` field is the `species_id`). `HABHUB_API_URL` is an environment variable, defaulting to `https://habhub-api.whoi.edu`. The list is cached for an hour per Lambda container. If the API is down, it keeps using the cached list; if there's no cached list, it raises an error so the SQS message is retried.
- **Image fields only:** `python manage.py backfill_summary_images --start_date=YYYY-MM-DD --end_date=YYYY-MM-DD [--species=A,B] [--workers=2]` adds `i` to existing documents from the target species' documents in `species-scores`, as partial updates. Run it for a new target species with `--species`, because the Lambda only starts writing a species' `i` values once it's a target species. `backfill_bin_species_summary` also adds `i` after rebuilding each month.
- **Histogram fields only:** `python manage.py backfill_summary_histograms --start_date=YYYY-MM-DD --end_date=YYYY-MM-DD [--workers=2]` adds `h` to existing documents from their `speciesScores` as partial updates, without re-aggregating `species-scores`.
- **Bulk size:** AWS OpenSearch limits requests to 10 MB on smaller instances, and summary documents are large, so the commands cap bulk requests at 5 MB.
- **Adding a field:** add it to both mapping definitions. Then run `create_summary_index()` against the existing index **before** deploying a Lambda that writes the field. Both commands call it. Otherwise OpenSearch maps the new field's keys automatically.

## How `/api/v2/ifcb-spatial-grid/` uses the summary

**List (the grid):** one `scripted_metric` aggregation on `bin-species-summary`, filtered
by date, dataset and bounding box. `GRID_MAP_SCRIPT` (in `ifcb_datasets/opensearch.py`)
runs once per Bin, using doc values only. It snaps `point` to the grid, applies the steps
below, and adds the result to its grid square. The response has one entry per square,
keyed `"{lng index}|{lat index}"`, where the grid point is `index * grid_level`. Django
only adds geohashes and builds the GeoJSON, so the response size depends on the number
of squares, not the length of the date range. A 2-year range takes about 2 seconds in
OpenSearch.

**Detail (one square):** one paged query on `bin-species-summary`, filtered to the
square's bounding box. It returns every Bin in the square, so Bins without a species
still show 0. It reads `binPid`, `sampleTime` and `point` through `docvalue_fields`,
with `_source: false`. The script field `BIN_RESULT_SCRIPT` returns each Bin's species
results, and `filter_path` keeps the response small. The view then keeps only the Bins
that snap to the requested square.

Both views run the same Painless function, `binResult()` (`BIN_RESULT_FUNCTION` in
`ifcb_datasets/opensearch.py`), so the agreement rule exists in one place. It checks model
agreement image by image, for each Bin and target species:

1. **Find each model's images of the species.** From the `i` fields, a model found an image if the species is its top class for that image, with a score at or above the species' threshold: `TargetSpecies.autoclass_threshold`, or `score_gte` if the request passes one.
2. **Count the votes for each image:** the number of models that found it.
3. **Work out how many votes an image needs.** It depends on the `agreement` param and N, the number of models that processed the Bin (`len(modelIds)`, after any `model_id` filter):

   | `agreement` | Votes needed | N = 1 | N = 3 | N = 5 | N = 6 |
   |---|---|---|---|---|---|
   | `any` | 1 | 1 | 1 | 1 | 1 |
   | `majority` (default) | more than half: ⌊N/2⌋ + 1 | 1 | 2 | 3 | 4 |
   | `strict` | more than 80%: ⌊4N/5⌋ + 1 | 1 | 3 | 5 | 5 |

   If only one model processed a Bin, its images count in every mode.
4. **Calculate the concentration:** `cell concentration = images with enough votes / mlAnalyzed * 1000` cells/L.

`modelsRequired` in the responses is the number of votes an image needed, and
`modelsAgreed` is the number of models that found at least one image of the species.

Example with 3 models, so `majority` needs 2 votes and `strict` needs 3:

| Image | 1 | 2 | 3 | 4 | 5 | 6 | Images counted |
|---|---|---|---|---|---|---|---|
| Model 1 | + | − | − | − | + | − | |
| Model 2 | − | + | − | − | + | − | |
| Model 3 | − | + | − | − | + | + | |
| Votes | 1 | 2 | 0 | 0 | 3 | 1 | |
| `any` | ✓ | ✓ | | | ✓ | ✓ | 4 |
| `majority` | | ✓ | | | ✓ | | 2 |
| `strict` | | | | | ✓ | | 1 |

So `any` is the union of the models' images, at least as many as any single model finds,
and `strict` keeps only the images nearly every model agrees on. Models often disagree
about individual images: for 20 September – 3 October 2026, the total concentration was
about 6 times lower with `majority` than with `any`, and 85 times lower with `strict`.

`geo_point` and `float` doc values are encoded, so `point` has about 1e-7° precision
loss. `mlAnalyzed` comes back as float32 (3.473 → 3.4730000495910645), and both the
script rounds it to 6 decimal places to get the original value back.
Rounding to the grid and of concentrations is half-even in both: `Math.rint` in Painless,
`round()` in Python.

Grid squares group Bins by snapping `point` to `grid_level` degrees, matching PostGIS
`ST_SnapToGrid()`. Each square's ID is the precision-5 geohash of its snapped point,
the same IDs as `/api/v1/ifcb-spatial-grid/`.

## How `/api/v2/ifcb-bins/` uses the indexes

The v2 version of `/api/v1/ifcb-bins/`, with the same `agreement`, `score_gte`,
`model_id` and `species` params as the spatial grid. Both views share
`ModelAgreementMixin` in `ifcb_datasets/api2/views.py`, and use the same
`binResult()` script.

- **List** (`/ifcb-bins/?start_date=...&end_date=...`): every Bin matching the date, dataset and bounding box filters, newest first. Reads `bin-species-summary` doc values and `binResult()`. Without `start_date`, it defaults to the past month (about 4,300 Bins, 4.5 MB), set by `default_date_range` on the viewset. The other v2 views default to the past year.
- **Detail** (`/ifcb-bins/{binPid}/`): one Bin, regardless of the date params, with `image_numbers` for each species: the images with enough votes, returned by `binResult()` with `includeImages`. Images are ordered by their number of votes, then by their highest score bucket, then by image number.
- **Species images** (`/ifcb-bins/{binPid}/get_species_images/?species=...`): v1 format. Up to 30 image links at `{dashboard URL}/{datasetId}/{imagePid}.png`. The dashboard URL comes from the HABhub Dataset, or `https://habon-ifcb.whoi.edu` if the Dataset isn't in the HABhub database.

Per species, `image_count` is the number of images with enough votes, the count behind
`cell_concentration`, so it always equals the length of `image_numbers` (and
`image_total` in species images).

## How `/api/v2/ifcb-bin-locations/` uses the summary

A lightweight endpoint for showing where Bins were sampled on a map. It returns one
GeoJSON Point per location with Bins matching the date, dataset and bounding box
params. The default range is the past year. There are no species or model agreement
params.

- **Query:** a `composite` aggregation on `bin-species-summary`, keyed on a `geotile_grid` of `point` at precision 29 (about 7 cm tiles). Only Bins at the same location are combined: a fixed station becomes one point, and a ship track becomes a point per Bin. The composite aggregation pages with `after_key`, so long date ranges can't hit the bucket limit.
- **Per location:** `geo_centroid` for the point, `min` and `max` of `sampleTime`, and up to 10 `datasetId` terms. `filter_path` returns only those fields.
- **Response:** each feature's `id` is the geotile key, and its properties are `bin_count`, `dataset_ids`, `start_time` and `end_time`. `metadata` has the `location_count` and `bin_count`.

Measured in October 2026: a year (36,756 Bins at 13,288 locations) took about 2 seconds
and 3.3 MB; all data (306,685 Bins at 50,476 locations) took about 7 seconds and 12 MB.
