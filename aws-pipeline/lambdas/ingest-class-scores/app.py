import json
import boto3
import h5py
import numpy
import requests
from datetime import datetime
from pathlib import Path
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

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


def lambda_handler(event, context):
    print(event)
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

        # get the model name from S3 key path
        try:
            model_name = s3_File_Name.split("/")[1]
        except:
            model_name = "unknown"

    except Exception as err:
        print(err)
        return {"statusCode": 400, "body": json.dumps("Error reading S3")}

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
                score_obj = {
                    "binPid": bin_pid,
                    "point": point,
                    "modelName": "model",
                    "mlAnalyzed": ml_analyzed,
                    "datasetId": metadata["primary_dataset"],
                    "sampleTime": metadata["timestamp_iso"],
                    "dateCreated": datetime.now().isoformat(),
                }
                print("score_obj", score_obj)
            else:
                print(f"Skip flag is true. Skip {bin_pid}")
                return None
        else:
            print(f"No metadata available on HABON IFCB. Skip {bin_pid}")
            return None
    except Exception as err:
        print(err)
        return None

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
                "modelName": {"type": "keyword"},
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
        )
        print("Connect to OS", os_client)
        info = os_client.info()
        print(
            f"Welcome to {info['version']['distribution']} {info['version']['number']}!"
        )

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
        f = h5py.File(f"/tmp/{s3_File_Name}", "r")
        print(list(f.keys()))
        # get the data frames
        scores = f["output_scores"]
        classes = f["class_labels"]
        rois = f["roi_numbers"]

        # calculate the species with the max score
        for index, score in enumerate(scores):
            max_index = numpy.argmax(score)
            max_value = score[max_index]
            species = classes[max_index].decode("UTF-8")
            roi = rois[index]
            # print(score)
            if species not in BLACKLIST:
                # print(species, max_value, roi)
                score_obj["species"] = species
                score_obj["score"] = max_value
                score_obj["imageNumber"] = roi
                score_obj["imagePid"] = f"{bin_pid}_{roi:05}"
                print(score_obj)

    except Exception as err:
        print(err)
        return None

    # TODO implement
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda and OS!")}
