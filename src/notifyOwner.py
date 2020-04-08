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
    iam_user = data.get("iamUser")
    iam_password = data.get("iamPassword")

    body_text = "New account with ID: {} was created successfully for you. A IAM User: {} with Password: {} has been created. Change password after first logon. Navigate to https://{}.signin.aws.amazon.com/console/ to sign in to the console.".format(
        account_id, iam_user, iam_password, account_id)

    body_html = """
        <html>
            <head></head>
            <body>
            <h1>New AWS account, {}, created successfully for you.</h1>
            <p>A user has been created for you.</p>
            <p>Username: {}</p>
            <p>Password: {}</p>
            <p>Change password at first login!</p>
            <p>Navigate to https://{}.signin.aws.amazon.com/console/ to sign in to the console.</p>
            </body>
        </html>
                """.format(account_id, iam_user, iam_password, account_id)

    sendEmail(os.environ['SENDER'], iam_user,
              "AWS Account was created", body_text, body_html)

    return data


def sendEmail(sender, recipient, subject, body_text, body_html):

    charset = "UTF-8"

    # Create a new SES resource and specify a region.
    client = get_boto_client('ses')

    # Try to send the email.
    # Provide the contents of the email.
    client.send_email(
        Destination={
            'ToAddresses': [
                recipient,
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': charset,
                    'Data': body_html,
                },
                'Text': {
                    'Charset': charset,
                    'Data': body_text,
                },
            },
            'Subject': {
                'Charset': charset,
                'Data': subject,
            },
        },
        Source=sender
    )
