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
    postErrorMessageToSns("Failure during account creation",
                          "There was an error during account creation. Check the logs for more details. ")
    return event


def postErrorMessageToSns(subject, message):
    sns_topic = os.environ['ERROR_SNS_TOPIC']
    client = boto3.client('sns')

    client.publish(
        TopicArn=sns_topic,
        Message=message,
        Subject=subject
    )
