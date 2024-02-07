# OpenSearch search code to Geohash Grid by field "point" and show details for each bucket
{
    "size": 0,
    "aggs": {
        "geohash_grid": {
            "geohash_grid": {"field": "point", "precision": 4},
            "aggs": {"details": {"top_hits": {"size": 50}}},
        }
    },
}
