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
    data = event[0]
    account_id = data.get("accountId")
    admin_account_role_name = data.get("adminAccountRole")
    admin_account_number = data.get("adminAccount")

    message = "New account with ID: {} was created successfully. Role: {} with Trust to Account: {} was setup for Admin Access.".format(
        account_id, admin_account_role_name, admin_account_number)
    debug_print(message)
    postMessageToSns("Account was created", message)

    return data


def postMessageToSns(subject, message):
    sns_topic = os.environ['ADMIN_SNS_TOPIC']
    client = boto3.client('sns')

    client.publish(
        TopicArn=sns_topic,
        Message=message,
        Subject=subject
    )
