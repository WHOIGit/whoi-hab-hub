import h5py
import numpy
from pathlib import Path
from opensearchpy import OpenSearch

BLACKLIST = [
    "nanoplankton_mix",
    "detritus",
    "detritus_transparent",
    "camera_spot",
    "bead",
    "bad",
    "fecal_pellet",
    "fiber",
    "fiber_TAG_external_detritus",
    "flagellate",
    "mix",
    "mix_elongated",
    "nanoplankton_mix",
    "pennate",
]
# get local data
bin_pid = Path("D20220906T024350_IFCB145_class.h5").stem
f = h5py.File("D20220906T024350_IFCB145_class.h5", "r")
print(list(f.keys()))
print(f["metadata"])
metadata = f["metadata"]
scores = f["output_scores"]
classes = f["class_labels"]
rois = f["roi_numbers"]

print("Scores Lenght", len(scores))
print("ROIS Lenght", len(rois))

for index, score in enumerate(scores):
    max_index = numpy.argmax(score)
    max_value = score[max_index]
    species = classes[max_index].decode("UTF-8")
    roi = rois[index]
    # print(score)
    """
    if species not in BLACKLIST:
        print(species, max_value, roi)
    """
print(bin_pid)

print(metadata.attrs.keys())
print(metadata.attrs["model_id"])

# connect to OS
"""
host = "localhost"
port = 9200
auth = ("admin", "admin")  # For testing only. Don't store credentials in code.

os_client = OpenSearch(
    hosts=[{"host": host, "port": port}],
    http_compress=True,  # enables gzip compression for request bodies
    http_auth=auth,
    verify_certs=False,
)

for doc in docs:
    response = os_client.index(index="scores-test", body=doc)
    print(response)



def insert_documents(documents):
    operations = []
    for document in documents:
        operations.append({"index": {"_index": "scores-test", "_id": document["osId"]}})
        operations.append(document)
    response = os_client.bulk(operations)
    print(response)
    return response
"""

# insert_documents(docs)
print("Bulk insert")
