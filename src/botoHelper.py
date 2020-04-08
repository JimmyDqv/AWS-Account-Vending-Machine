import boto3


def get_boto_client(service, access_key=None, secret_access_key=None, session_token=None):
    client = boto3.client(
        service,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token
    )
    return client
