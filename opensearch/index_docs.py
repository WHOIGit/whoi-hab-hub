import requests
from opensearchpy import OpenSearch

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
    print(response)
"""


def insert_documents(documents):
    operations = []
    for document in documents:
        operations.append({"index": {"_index": "scores-test", "_id": document["osId"]}})
        operations.append(document)
    response = os_client.bulk(operations)
    print(response)
    return response


insert_documents(docs)
print("Bulk insert")
