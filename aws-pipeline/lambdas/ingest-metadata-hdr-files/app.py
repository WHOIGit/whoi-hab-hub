import json
import boto3
import os
from pathlib import Path
from decimal import Decimal
from hdr import parse_hdr_file

s3_client = boto3.client("s3")


def lambda_handler(event, context):
    print(event)
    # parse the S3 file received
    try:
        s3_Bucket_Name = event["Records"][0]["s3"]["bucket"]["name"]
        s3_File_Name = event["Records"][0]["s3"]["object"]["key"]
        print(s3_File_Name)
        # get the Bin pid
        bin_pid = Path(s3_File_Name).stem
        # set local file path
        file_path = f"/tmp/{s3_File_Name}"

        # download file to tmp directory
        result = s3_client.download_file(s3_Bucket_Name, s3_File_Name, file_path)

        # parse HDR file with HDR utilities
        resp = parse_hdr_file(file_path)
        latitude = resp.get("gpsLatitude", None)
        longitude = resp.get("gpsLongitude", None)

        if latitude and longitude:
            print(latitude, longitude)
            # run the Dynamo update
            dynamodb = boto3.resource("dynamodb")
            table_name = "habhub-bins-metadata"
            table = dynamodb.Table(table_name)

            try:
                print("saving to Dynamo...")
                # Dynamo needs float converted to Decimal for N type
                response = table.update_item(
                    Key={
                        "pid": bin_pid,
                    },
                    UpdateExpression="SET latitude = :latitude, longitude = :longitude",
                    ExpressionAttributeValues={
                        ":latitude": Decimal(str(latitude)),
                        ":longitude": Decimal(str(longitude)),
                    },
                    ReturnValues="UPDATED_NEW",
                )
                print(f"{bin_pid} saved")
                print(response)
            except Exception as err:
                print(err)
        else:
            print("No lat/long")

        # delete file from tmp dir
        os.remove(file_path)
        # delete file from S3
        s3_client.delete_object(Bucket=s3_Bucket_Name, Key=s3_File_Name)
        print("file deleted")

    except Exception as err:
        print(err)
        return None

    # TODO implement
    return {
        "statusCode": 200,
        "body": json.dumps(f"{bin_pid} HDR data saved to Dynamo"),
    }
