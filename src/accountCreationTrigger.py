import os
import sys
import boto3
import botocore
import json
import time
from debug import debug_print
from debug import error_print
from botoHelper import get_boto_client


def handler(event, context):
    debug_print(json.dumps(event, indent=2))
    s3_event = event["Records"][0]["s3"]
    s3_bucket = s3_event["bucket"]["name"]
    s3_object = s3_event["object"]["key"]

    client = get_boto_client("s3")
    response = client.get_object(Bucket=s3_bucket, Key=s3_object)
    content = json.loads(response['Body'].read().decode('utf-8'))
    debug_print(json.dumps(content, indent=2))

    step_function_arn = os.environ["ACCOUNT_CREATOR_STEPFUNCTION"]
    invoke_statemachine(step_function_arn, content)


def invoke_statemachine(arn, input):
    client = get_boto_client("stepfunctions")
    account_name = input.get("accountName")
    response = client.start_execution(
        stateMachineArn=arn,
        name="{}-creation-{}".format(account_name, time.time()),
        input=json.dumps(input)
    )
    debug_print(response)
    return(response)
