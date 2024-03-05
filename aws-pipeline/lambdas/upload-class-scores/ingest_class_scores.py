import json
import boto3
import h5py

s3_client = boto3.client("s3")


def lambda_handler(event, context):
    print(event)
    try:
        s3_Bucket_Name = event["Records"][0]["s3"]["bucket"]["name"]
        s3_File_Name = event["Records"][0]["s3"]["object"]["key"]

        object = s3_client.get_object(Bucket=s3_Bucket_Name, Key=s3_File_Name)
        body = object["Body"]
        h5_string = body.read().decode("utf-8")
        f = h5py.File(h5_string, "r")
        print(list(f.keys()))

    except Exception as err:
        print(err)

    # TODO implement
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
