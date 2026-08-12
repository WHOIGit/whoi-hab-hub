import hashlib
import json


def create_cache_key(request, pk=0):
    """
    Build a cache key from the request path, a hash of its query params, and an
    optional object pk (so per-object results, e.g. one per Dataset in a list
    response, don't collide with each other).
    """
    qp_encoded = json.dumps(request.query_params, sort_keys=True).encode()
    qp_hash = hashlib.md5(qp_encoded)
    return f"{request.path}:{qp_hash.hexdigest()}:{pk}"
