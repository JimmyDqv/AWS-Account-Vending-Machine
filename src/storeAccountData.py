import os
import sys
import boto3
import json
import time
from debug import debug_print
from debug import error_print
from botoHelper import get_boto_client


def handler(event, context):
    debug_print(json.dumps(event, indent=2))
    return main(event)


def main(event):
    bucket = os.environ["ACCOUNT_DATA_BUCKET"]
    ou = event.get("ouName")
    account_id = event.get("accountId")
    account_name = event.get("accountName")
    account_id = event.get("accountId")
    client = get_boto_client('s3')
    client.put_object(
        Body=json.dumps(event),
        Bucket=bucket,
        Key="{}/{}/{}.json".format(ou, account_name, account_id),
        ServerSideEncryption='AES256'
    )

    return event
