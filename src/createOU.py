import os
import sys
import boto3
import botocore
import json
import time
from debug import debug_print
from botoHelper import get_boto_client


def handler(event, context):
    debug_print(json.dumps(event, indent=2))
    return main(event)


def main(event):
    ou_name = event.get("ouName")
    debug_print("OU Name: {}".format(ou_name))
    root_ou_id = get_organization_root_id()
    debug_print("Root OU ID: {}".format(root_ou_id))
    new_ou_id = create_organizational_unit(root_ou_id, ou_name)
    debug_print("New OU ID: {}".format(new_ou_id))

    event["rootOuId"] = root_ou_id
    event["ouId"] = new_ou_id

    return event


def get_organization_root_id():
    client = get_boto_client("organizations")
    response = client.list_roots()
    # debug_print(response)
    root_id = response['Roots'][0]['Id']

    return root_id


def create_organizational_unit(root_ou_id, ou_name):
    debug_print("Creating new OU if needed with name {}".format(ou_name))

    ou_id = get_ou_id_for_name(root_ou_id, ou_name)
    if ou_id == None:
        client = get_boto_client("organizations")
        response = client.create_organizational_unit(
            ParentId=root_ou_id,
            Name=ou_name
        )
        new_ou_id = response["OrganizationalUnit"]["Id"]
        debug_print("Created OU with ID: {}".format(new_ou_id))
        return new_ou_id

    debug_print("OU already existed. ID: {}".format(ou_id))
    return ou_id


def get_ou_id_for_name(root_id, ou_name):
    debug_print("get id for {} in {}".format(ou_name, root_id))
    client = get_boto_client("organizations")
    response = client.list_organizational_units_for_parent(
        ParentId=root_id,
        MaxResults=10)
    ous = response["OrganizationalUnits"]
    for ou in ous:
        if ou["Name"] == ou_name:
            return ou["Id"]

    while('NextToken' in response):
        response = client.list_organizational_units_for_parent(
            ParentId=root_id,
            MaxResults=50,
            NextToken=response['NextToken']
        )
        ous = response["OrganizationalUnits"]
        for ou in ous:
            if ou["Name"] == ou_name:
                return True

    return None
