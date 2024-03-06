import json
import boto3
import h5py

s3_client = boto3.client("s3")


def lambda_handler(event, context):
    print(event)
    try:
        s3_Bucket_Name = event["Records"][0]["s3"]["bucket"]["name"]
        s3_File_Name = event["Records"][0]["s3"]["object"]["key"]

        # download file to tmp directory
        result = s3_client.download_file(
            s3_Bucket_Name, s3_File_Name, f"/tmp/{s3_File_Name}"
        )
        f = h5py.File(f"/tmp/{s3_File_Name}", "r")
        print(list(f.keys()))

    except Exception as err:
        print(err)

    # TODO implement
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
