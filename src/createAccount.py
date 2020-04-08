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
    return main(event)


def main(event):
    account_name = event.get("accountName")
    account_email = event.get("accountEmail")
    account_role = event.get("accountRole")

    account_request_id = create_account(
        account_name, account_email, account_role)

    event["accountRequestId"] = account_request_id
    return event


def create_account(name, email, role):
    account_request_id = None
    client = get_boto_client('organizations')

    debug_print(
        "Creating account with {} name and e-mail {}".format(name, email))
    response = client.create_account(Email=email, AccountName=name,
                                     RoleName=role,
                                     IamUserAccessToBilling="ALLOW")
    account_request_id = response['CreateAccountStatus']['Id']

    return account_request_id
