import requests
from opensearchpy import OpenSearch, helpers

# get local data
api_url = "http://localhost:8000/api/v1/scores/"
response = requests.get(api_url)
print(response.status_code, response.url)
data = response.json()
docs = data["results"]
print(docs)

# connect to OS
host = "localhost"
port = 9200
auth = ("admin", "admin")  # For testing only. Don't store credentials in code.

os_client = OpenSearch(
    hosts=[{"host": host, "port": port}],
    http_compress=True,  # enables gzip compression for request bodies
    http_auth=auth,
    verify_certs=False,
)
"""
for doc in docs:
    response = os_client.index(index="scores-test", body=doc)



def insert_documents(documents):
    operations = []
    for document in documents:
        operations.append({"index": {"_index": "scores-test", "_id": document["osId"]}})
        operations.append(document)
    response = os_client.bulk(operations)
    print(response)
    return response
    print(response)
"""


def upsert_documents(documents):
    operations = []
    for document in documents:
        doc_id = document["osId"]
        operations.append(
            {
                "_op_type": "update",
                "_index": "scores-test",
                "_id": doc_id,
                "doc": document,
                "doc_as_upsert": True,
            }
        )
    response = helpers.bulk(os_client, operations, index="scores-test", max_retries=3)
    print(response)
    return response


# insert_documents(docs)
# print("Bulk insert")

upsert_documents(docs)
print("Bulk upsert ", len(docs))
