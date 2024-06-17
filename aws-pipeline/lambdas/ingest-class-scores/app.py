import json
import boto3
import h5py
import numpy
from pathlib import Path
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

s3_client = boto3.client("s3")


def lambda_handler(event, context):
    print(event)
    # parse the S3 file received
    try:
        s3_Bucket_Name = event["Records"][0]["s3"]["bucket"]["name"]
        s3_File_Name = event["Records"][0]["s3"]["object"]["key"]
        print(s3_File_Name)
        # download file to tmp directory
        result = s3_client.download_file(
            s3_Bucket_Name, s3_File_Name, f"/tmp/{s3_File_Name}"
        )
        # get the Bin pid
        bin_pid = Path(s3_File_Name).stem
        # read file into h5py
        f = h5py.File(f"/tmp/{s3_File_Name}", "r")
        print(list(f.keys()))
        # get the data frames
        scores = f["output_scores"]
        classes = f["class_labels"]
        rois = f["roi_numbers"]

        # calculate the species with the max score
        for score in scores:
            max_index = numpy.argmax(score)
            max_value = score[max_index]
            species = classes[max_index].decode("UTF-8")
            roi = rois[max_index]
            print(species, max_value, roi)

        print("Bin pid:", bin_pid)

    except Exception as err:
        print(err)

    host = "vpc-habhub-prod-3jxcbqq7ogktcoym3jnmjhgxsi.us-east-1.es.amazonaws.com"  # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
    region = "us-east-1"
    service = "es"
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region, service)

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
    except Exception as err:
        print(err)

    # TODO implement
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda and OS!")}
