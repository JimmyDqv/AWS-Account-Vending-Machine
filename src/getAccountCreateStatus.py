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
    account_request_id = event.get("accountRequestId")
    account_status = get_account_creation_status(account_request_id)
    state = account_status["CreateAccountStatus"]["State"]
    account_id = account_status["CreateAccountStatus"]["AccountId"]
    event["createAccountStatus"] = state
    event["accountId"] = account_id

    return event


def get_account_creation_status(account_request_id):
    client = get_boto_client('organizations')
    response = client.describe_create_account_status(
        CreateAccountRequestId=account_request_id
    )
    return response
