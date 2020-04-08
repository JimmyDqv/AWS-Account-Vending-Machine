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
    root_ou_id = event.get("rootOuId")
    ou_id = event.get("ouId")
    account_id = event.get("accountId")

    move_account(root_ou_id, ou_id, account_id)

    return event


def move_account(root_ou_id, ou_id, account_id):
    client = get_boto_client('organizations')
    debug_print("Trying to move account....")
    client.move_account(
        AccountId=account_id,
        SourceParentId=root_ou_id,
        DestinationParentId=ou_id
    )
