import h5py
import numpy
from pathlib import Path
from opensearchpy import OpenSearch

# get local data
bin_pid = Path("D20220906/D20220906T004515_IFCB145_class.h5").stem
f = h5py.File("D20220906/D20220906T004515_IFCB145_class.h5", "r")
print(list(f.keys()))
scores = f["output_scores"]
classes = f["class_labels"]
rois = f["roi_numbers"]

for score in scores:
    max_index = numpy.argmax(score)
    max_value = score[max_index]
    species = classes[max_index].decode("UTF-8")
    roi = rois[max_index]
    print(species, max_value, roi)

print(bin_pid)

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


# insert_documents(docs)
print("Bulk insert")
