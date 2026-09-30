# HABhub OpenSearch indexes

HABhub stores IFCB classifier results in two indexes on the `habhub-production`
OpenSearch domain:

| Index | One document per | Written by | Read by |
|---|---|---|---|
| `species-scores` | image (ROI) per model | `ingest-class-scores-sqs` Lambda | `/api/v2/ifcb-species-scores/`, `/api/v2/ifcb-fixed-metrics/` |
| `bin-species-summary` | Bin | `ingest-class-scores-sqs` Lambda, `backfill_bin_species_summary` command | `/api/v2/ifcb-spatial-grid/` |

`species-scores` is the raw data (about 1.6 billion documents). `bin-species-summary`
is a per-Bin rollup of it (about 306,000 documents), so the spatial grid can be served
without aggregating millions of image documents on every request.

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

Settings: 1 shard, 1 replica.
Defined in `habhub-dataserver/habhub/ifcb_datasets/opensearch.py`, with a copy in
`aws-pipeline/lambdas/ingest-class-scores-sqs/app.py`. Keep the two in sync.

```json
{
  "properties": {
    "binPid":        { "type": "keyword" },
    "datasetId":     { "type": "keyword" },
    "sampleTime":    { "type": "date" },
    "dateUpdated":   { "type": "date" },
    "point":         { "type": "geo_point" },
    "mlAnalyzed":    { "type": "float" },
    "modelIds":      { "type": "keyword" },
    "speciesCounts": { "type": "object", "enabled": false },
    "speciesScores": { "type": "object", "enabled": false }
  }
}
```

`speciesCounts` and `speciesScores` have `"enabled": false`. They're kept in `_source`
but not indexed, so their species and model keys don't add fields to the mapping. The
catch is that they can't be used in queries or aggregations, not even `exists`. Filter
on the other fields and read these from `_source`.

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
| `dateUpdated` | Last time the document was written |

About `speciesScores`:
- **Buckets:** each is 0.01 wide: `bucket = floor(score * 100)`, from 0 to 99, where 99 holds scores of 0.99–1.00. Only non-empty buckets are stored, in ascending order.
- **Totals:** a histogram's counts add up to the matching `speciesCounts` value.
- **Thresholds:** to count images scoring at or above a threshold `t`, sum the buckets that are ≥ `round(t * 100)`. Because the buckets are 0.01 wide, this is exact for any 2-decimal threshold, which is the precision of `TargetSpecies.autoclass_threshold`.
- **float32 rounding:** scores are float32, so 0.7 is stored as 0.69999999. The Lambda's `score_bucket()` and the backfill's histogram `offset` both add a small offset so a score like this lands in bucket 70, not 69.

### How it's written

- **Lambda:** `ingest-class-scores-sqs` processes one H5 file, meaning one Bin and one model. It merges that model's counts and histograms into the Bin's document with a script update, using `retry_on_conflict` because several models' files for the same Bin can arrive at once. It removes that model's old values first, so re-ingesting a file is safe.
- **Backfill:** `python manage.py backfill_bin_species_summary --start_date=YYYY-MM-DD --end_date=YYYY-MM-DD [--chunk_hours=1] [--workers=4]` rebuilds documents from `species-scores`, replacing each one completely. A Lambda update to the same Bin during a backfill can be overwritten, so re-run the last few days afterwards.
- **Adding a field:** add it to both mapping definitions. Then run `create_summary_index()` (the backfill command calls it) against the existing index **before** deploying a Lambda that writes the field. Otherwise OpenSearch maps the new field's keys automatically.

## How `/api/v2/ifcb-spatial-grid/` uses the summary

For each Bin and target species:

1. **Count the images at or above the threshold** for each model, using `speciesScores`. The threshold is the species' `TargetSpecies.autoclass_threshold`, or `score_gte` if the request passes one.
2. **Count the agreeing models.** A model agrees if its count is above 0.
3. **Work out how many models must agree.** It's `min_models` (default 3). If fewer models processed the Bin (`len(modelIds)`), all of them must agree instead, unless the request has `strict_agreement=true`.
4. **Calculate the concentration.** If enough models agree: `cell concentration = mean(agreeing counts) / mlAnalyzed * 1000` cells/L. Otherwise the value is 0.

Worked example, using the Bin above (5 models ran, so 3 must agree):

| Species | Threshold | Count per model at or above threshold | Agreeing models | Cell concentration |
|---|---|---|---|---|
| Pseudo-nitzschia | 0.00 | AKsup2 2, Tripos1 1, Tripos2 1 | 3 | (4 / 3) / 3.936 × 1000 = **339 cells/L** |
| Pseudo-nitzschia | 0.85 | AKsup2 2 (buckets 87, 97), Tripos1 1 (89), Tripos2 0 (83) | 2 | **0** (fewer than 3) |
| Karenia | any | only GoM3 and Tripos2 found it | at most 2 | **0** (fewer than 3) |

Grid squares group Bins by snapping `point` to `grid_level` degrees, matching PostGIS
`ST_SnapToGrid()`. Each square's ID is the precision-5 geohash of its snapped point,
the same IDs as `/api/v1/ifcb-spatial-grid/`.
