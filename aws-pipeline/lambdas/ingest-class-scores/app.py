import json
import boto3
import h5py
import numpy
import requests
import os
from datetime import datetime
from pathlib import Path
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth, helpers

s3_client = boto3.client("s3")

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


def upsert_documents(documents, index_name, os_client):
    operations = []
    for document in documents:
        # print(document)
        doc_id = document["osId"]
        operations.append(
            {
                "_op_type": "update",
                "_index": index_name,
                "_id": doc_id,
                "doc": document,
                "doc_as_upsert": True,
            }
        )
    response = helpers.bulk(os_client, operations, index=index_name, max_retries=3)
    print(response)
    return response


def lambda_handler(event, context):
    print(event)
    lambda_resp = None
    # parse the S3 file received
    try:
        s3_Bucket_Name = event["Records"][0]["s3"]["bucket"]["name"]
        s3_File_Name = event["Records"][0]["s3"]["object"]["key"]
        print(s3_File_Name)
        # get the Bin pid
        file_name = Path(s3_File_Name).stem
        file_path = f"/tmp/{file_name}.h5"
        # download file to tmp directory
        result = s3_client.download_file(s3_Bucket_Name, s3_File_Name, file_path)

        bin_pid = file_name.replace("_class", "")
        print("Bin pid:", bin_pid)

        # get the model name from S3 key path in case missing from metadata
        try:
            model_id = s3_File_Name.split("/")[1]
        except:
            model_id = "unknown"
        print("Model id:", model_id)

    except Exception as err:
        print(err)
        lambda_resp = {"statusCode": 400, "body": json.dumps("Error reading S3")}

    # Get Dynamo metadata record
    """
    try:
        dynamodb = boto3.resource("dynamodb")
        table_name = "habhub-bins-metadata"
        table = dynamodb.Table(table_name)
        # get metadata item from database
        test_bin = "D20200309T180635_IFCB124"
        item = table.get_item(Key={"pid": "D20200309T180635_IFCB124"})
        print("Metadata", item)
        metadata = item.get("Item", None)
        print(metadata)
    except Exception as err:
        print(err)
        return None
    """

    # continue processing if error is null
    if not lambda_resp:
        # Get metadata from HABON IFCB dashboard
        test_bin = "D20200309T180635_IFCB124"
        dashboard_url = f"https://habon-ifcb.whoi.edu/api/bin/{bin_pid}"
        try:
            response = requests.get(dashboard_url)
            print(response)
            if response.status_code == 200:
                print(response.json())
                metadata = response.json()
                # check for Skip flag
                if not metadata["skip"]:
                    # parse ml_analyzed to just get the float
                    ml_analyzed = float(metadata["ml_analyzed"].split(" ")[0])
                    print("ml_analyzed", ml_analyzed)
                    point = [metadata["lng"], metadata["lat"]]
                    metadata_obj = {
                        "binPid": bin_pid,
                        "point": point,
                        "mlAnalyzed": ml_analyzed,
                        "datasetId": metadata["primary_dataset"],
                        "sampleTime": metadata["timestamp_iso"],
                        "dateCreated": datetime.now().isoformat(),
                    }
                    print("metadata_obj", metadata_obj)
                else:
                    print(f"Skip flag is true. Skip {bin_pid}")
                    return None
            else:
                print(f"No metadata available on HABON IFCB. Skip {bin_pid}")
                return None
        except Exception as err:
            print(err)
            lambda_resp = {
                "statusCode": 400,
                "body": json.dumps("Error connecting to Habon-IFCB"),
            }

    if not lambda_resp:
        # Connect to OS for indexing
        host = "vpc-habhub-prod-3jxcbqq7ogktcoym3jnmjhgxsi.us-east-1.es.amazonaws.com"  # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
        region = "us-east-1"
        service = "es"
        credentials = boto3.Session().get_credentials()
        auth = AWSV4SignerAuth(credentials, region, service)
        # Create an index with non-default settings.
        index_name = "species-scores"
        # mapping dictionary that contains the settings and
        # _mapping schema for a new Elasticsearch index:
        # _id = binPid_imageNumber_modelName
        index_body = {
            "settings": {"number_of_shards": 2, "number_of_replicas": 1},
            "mappings": {
                "properties": {
                    "binPid": {"type": "keyword"},
                    "imageNumber": {"type": "keyword"},
                    "imagePid": {"type": "keyword"},
                    "score": {"type": "float"},
                    "modelId": {"type": "keyword"},
                    "species": {"type": "keyword"},
                    "sampleTime": {"type": "date"},
                    "dateCreated": {"type": "date"},
                    "datasetId": {"type": "keyword"},
                    "point": {"type": "geo_point"},
                    "mlAnalyzed": {"type": "float"},
                }
            },
        }

        try:
            os_client = OpenSearch(
                hosts=[{"host": host, "port": 443}],
                http_auth=auth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                pool_maxsize=20,
                timeout=20,
            )
            print("Connect to OS", os_client)
            info = os_client.info()
            print(info)

            # create index if it's missing
            if not os_client.indices.exists(index=index_name):
                print("No Index")
                # response = os_client.indices.delete(index=index_name, ignore_unavailable=True)
                response = os_client.indices.create(index_name, body=index_body)
                print("\nCreating index:")
                print(response)
            else:
                print("Index Exists")
                test_response = os_client.indices.get(index_name)
                print(test_response)

            # parse the H5 file and index results
            # read file into h5py
            f = h5py.File(file_path, "r")
            print(list(f.keys()))
            # get the data frames
            metadata = f["metadata"]
            scores = f["output_scores"]
            classes = f["class_labels"]
            rois = f["roi_numbers"]

            """
            try:
                model_id = metadata.attrs["model_id"]
            except Exception as err:
                print(err)
                print("model_id missing from metadata, set from S3 key")
            """

            documents = []
            # calculate the species with the max score
            for index, score in enumerate(scores):
                max_index = numpy.argmax(score)
                max_value = score[max_index]
                species = classes[max_index].decode("UTF-8")
                roi = rois[index]
                # print(score)

                score_obj = {}
                # print(species, max_value, roi)
                score_obj["species"] = species
                score_obj["score"] = max_value
                score_obj["imageNumber"] = roi
                score_obj["imagePid"] = f"{bin_pid}_{roi:05}"
                score_obj["modelId"] = model_id
                score_obj["osId"] = f"{bin_pid}_{roi:05}_{model_id}"
                document_obj = metadata_obj | score_obj
                documents.append(document_obj)

            # insert or update document into OpenSearch
            print("Start upsert ", len(documents))
            upsert_documents(documents, index_name, os_client)
            print("Bulk upsert ", len(documents))

        except Exception as err:
            print(err)
            lambda_resp = {
                "statusCode": 400,
                "body": json.dumps("Error indexing documents"),
            }

    # clean up and return response
    # delete file from tmp dir
    os.remove(file_path)
    # delete file from S3
    response = s3_client.delete_object(Bucket=s3_Bucket_Name, Key=s3_File_Name)
    print("file deleted", s3_Bucket_Name, s3_File_Name)
    return {"statusCode": 200, "body": json.dumps(f"{bin_pid} successfully indexed")}
