import json
import boto3
import os
from pathlib import Path
from decimal import Decimal

# import IFCB utilities from https://github.com/joefutrelle/pyifcb package
from ifcb.data.adc import AdcFile
from ifcb.metrics.ml_analyzed import compute_ml_analyzed_adc

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

        # download file to tmp directory
        result = s3_client.download_file(
            s3_Bucket_Name, s3_File_Name, f"/tmp/{bin_pid}.adc"
        )

        # get the dataset id from S3 key path
        try:
            dataset = s3_File_Name.split("/")[1]
        except:
            dataset = "unknown"

        # parse file with pyifcb package
        adc = AdcFile(f"/tmp/{bin_pid}.adc")
        print(adc, dataset)
        ml_results = compute_ml_analyzed_adc(adc)
        ml_analyzed = ml_results[0]
        print(ml_analyzed)
        # delete file from tmp dir
        os.remove(f"/tmp/{bin_pid}.adc")
        # delete file from S3
        s3_client.delete_object(Bucket=s3_Bucket_Name, Key=s3_File_Name)
        print("file deleted")

    except Exception as err:
        print(err)
        return None

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
            UpdateExpression="SET ml_analyzed = :ml_analyzed, dataset = :dataset",
            ExpressionAttributeValues={
                ":ml_analyzed": Decimal(str(ml_analyzed)),
                ":dataset": dataset,
            },
            ReturnValues="UPDATED_NEW",
        )
        print(f"{bin_pid} saved")
        print(response)
    except Exception as err:
        print(err)
        return None

    # TODO implement
    return {
        "statusCode": 200,
        "body": json.dumps(f"{bin_pid} ADC data saved to Dynamo"),
    }
