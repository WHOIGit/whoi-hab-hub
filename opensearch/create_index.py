from opensearchpy import OpenSearch

host = "localhost"
port = 9200
auth = ("admin", "admin")  # For testing only. Don't store credentials in code.

os_client = OpenSearch(
    hosts=[{"host": host, "port": port}],
    http_compress=True,  # enables gzip compression for request bodies
    http_auth=auth,
    verify_certs=False,
)

# Create an index with non-default settings.
index_name = "score-test"
# mapping dictionary that contains the settings and
# _mapping schema for a new Elasticsearch index:
index_body = {
    "settings": {"number_of_shards": 2, "number_of_replicas": 1},
    "mappings": {
        "properties": {
            "image_pid": {"type": "keyword"},
            "score": {"type": "float"},
            "model_name": {"type": "keyword"},
            "species": {"type": "keyword"},
            "bin_pid": {"type": "keyword"},
            "sample_time": {"type": "date"},
            "date_created": {"type": "date"},
            "dataset_id": {"type": "keyword"},
            "point": {"type": "geo_point"},
        }
    },
}

response = os_client.indices.delete(index=index_name, ignore_unavailable=True)
print("\nDeleting index:")
print(response)

response = os_client.indices.create(index_name, body=index_body)
print("\nCreating index:")
print(response)

# Delete the index.
# response = os_client.indices.delete(index=index_name)

# print("\nDeleting index:")
# print(response)
