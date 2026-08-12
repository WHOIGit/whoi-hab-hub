import hashlib
import json

from django.core.cache import cache


def create_cache_key(request, pk=0):
    """
    Build a cache key from the request path, a hash of its query params, and an
    optional object pk (so per-object results, e.g. one per Dataset in a list
    response, don't collide with each other).
    """
    qp_encoded = json.dumps(request.query_params, sort_keys=True).encode()
    qp_hash = hashlib.md5(qp_encoded)
    return f"{request.path}:{qp_hash.hexdigest()}:{pk}"


# Cache keys for Dataset.get_max_mean_values() are scoped by dataset id (rather
# than by request.path, like create_cache_key() above) so a single dataset's
# entries can be targeted with delete_pattern() without touching other datasets,
# and so the list and detail endpoints can share a cached result for the same
# dataset/query-params.
DATASET_SUMMARY_CACHE_PREFIX = "dataset-max-mean-values"


def create_dataset_summary_cache_key(request, dataset_id):
    qp_encoded = json.dumps(request.query_params, sort_keys=True).encode()
    qp_hash = hashlib.md5(qp_encoded).hexdigest()
    return f"{DATASET_SUMMARY_CACHE_PREFIX}:{dataset_id}:{qp_hash}"


def clear_dataset_summary_cache(dataset_id):
    cache.delete_pattern(f"{DATASET_SUMMARY_CACHE_PREFIX}:{dataset_id}:*")


def clear_spatial_grid_cache():
    """
    BinSpatialGridViewSet results aren't scoped to a single Dataset (a grid square
    can combine bins from multiple datasets), so they can't be targeted per-dataset
    like the dataset summary cache above. Clear just this endpoint's cache entries
    instead of the whole cache (django.core.cache.cache.clear() also wipes sessions,
    since SESSION_CACHE_ALIAS shares the "default" cache).
    """
    cache.delete_pattern("*ifcb-spatial-grid*")
