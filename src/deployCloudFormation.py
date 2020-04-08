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
    account_id = event.get("accountId")
    account_role = event.get("accountRole")

    credentials = assume_role(account_id, account_role)

    access_key = credentials['AccessKeyId']
    secret_access_key = credentials['SecretAccessKey']
    session_token = credentials['SessionToken']
    cfn_client = get_boto_client("cloudformation", access_key,
                                 secret_access_key, session_token)

    templates = event["cfnTemplates"]
    for template in templates:
        deploy_cloudformation_template(cfn_client, template, event)

    return event


def deploy_cloudformation_template(cfn_client, template, event):
    bucket = os.environ['CLOUDFORMATION_TEMPLATE_BUCKET']
    templateName = template["templateName"]
    stackName = template["stackName"]
    debug_print("Deploying CFN Template: {}".format(templateName))
    parameters = create_cloudformation_parameters(
        template["parameters"], event)
    debug_print(json.dumps(parameters, indent=2))
    presigned_url = create_s3_presigned_url(bucket, templateName)
    debug_print(presigned_url)
    if not cloudformation_stack_exists(cfn_client, stackName, "eu-west-1"):
        create_cloudformation_stack(
            cfn_client, presigned_url, stackName, "eu-west-1", parameters)
    else:
        update_cloudformation_stack(
            cfn_client, presigned_url, stackName, "eu-west-1", parameters)


def create_cloudformation_parameters(parameters, event):
    cfnParams = []
    for parameter in parameters:
        key = parameter["key"]
        value = parameter["value"]
        if value.startswith("{{") and value.endswith("}}"):
            value = value[2:len(value)-2]
            value = event.get(value)

        cfnParams.append({
            'ParameterKey': key,
            'ParameterValue':  value
        })
    return cfnParams


def assume_role(account_id, role_name):
    debug_print("Assuming role.....")
    role_arn = "arn:aws:iam::{0}:role/{1}".format(account_id, role_name)
    client = get_boto_client('sts')
    assumed_role = client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="account_vending_machine_lambda"
    )

    return assumed_role['Credentials']


def create_s3_presigned_url(bucket, object):
    client = get_boto_client('s3')
    response = client.generate_presigned_url('get_object',
                                             Params={
                                                 'Bucket': bucket,
                                                 'Key': object
                                             },
                                             ExpiresIn=3600)
    return response


def create_cloudformation_stack(client, template_url, stackname, stackregion, parameters):
    create_date = time.strftime("%d/%m/%Y")

    response = client.create_stack(
        StackName=stackname,
        TemplateURL=template_url,
        Parameters=parameters,
        NotificationARNs=[],
        Capabilities=[
            'CAPABILITY_NAMED_IAM',
        ],
        OnFailure='ROLLBACK',
        Tags=[
            {
                'Key': 'CreatedBy',
                'Value': 'Account-Vending-Machine'
            },
            {
                'Key': 'CreatedAt',
                'Value': create_date
            }
        ]
    )
    debug_print("Stack creation in process...")
    debug_print(response)
    stack_creating = True
    while stack_creating is True:
        event_list = client.describe_stack_events(
            StackName=stackname).get("StackEvents")
        stack_event = event_list[0]

        if (stack_event.get('ResourceType') == 'AWS::CloudFormation::Stack' and
                stack_event.get('ResourceStatus') == 'CREATE_COMPLETE'):
            stack_creating = False
            debug_print("Stack creation completed!")
        elif (stack_event.get('ResourceType') == 'AWS::CloudFormation::Stack' and
                stack_event.get('ResourceStatus') == 'ROLLBACK_COMPLETE'):
            stack_creating = False
            debug_print("Stack construction failed!!")
        else:
            debug_print("Stack creating...")
            time.sleep(5)


def update_cloudformation_stack(client, template_url, stackname, stackregion, parameters):
    debug_print("Updating stack: {}".format(stackname))
    try:
        update_date = time.strftime("%d/%m/%Y")

        response = client.update_stack(
            StackName=stackname,
            TemplateURL=template_url,
            Parameters=parameters,
            NotificationARNs=[],
            Capabilities=[
                'CAPABILITY_NAMED_IAM',
            ],
            Tags=[
                {
                    'Key': 'CreatedBy',
                    'Value': 'Account-Vending-Machine'
                },
                {
                    'Key': 'UpdatedAt',
                    'Value': update_date
                }
            ]
        )
        debug_print("Stack update in process...")
        debug_print(response)
        stack_updating = True
        while stack_updating is True:
            event_list = client.describe_stack_events(
                StackName=stackname).get("StackEvents")
            stack_event = event_list[0]

            if (stack_event.get('ResourceType') == 'AWS::CloudFormation::Stack' and
                    stack_event.get('ResourceStatus') == 'UPDATE_COMPLETE'):
                stack_updating = False
                debug_print("Stack update completed!")
            elif (stack_event.get('ResourceType') == 'AWS::CloudFormation::Stack' and
                    stack_event.get('ResourceStatus') == 'UPDATE_ROLLBACK_COMPLETE'):
                stack_updating = False
                debug_print("Stack update failed!!")
            else:
                debug_print("Stack updating...")
                time.sleep(5)
    except Exception as e:
        message = getattr(e, 'message', str(e))
        # debug_print("------------------------------------")
        # debug_print(message)
        # debug_print("------------------------------------")
        if "No updates are to be performed" not in message:
            raise e
        else:
            debug_print("Stack already up to date!")


def cloudformation_stack_exists(client, stackname, stackregion):
    try:
        client.describe_stacks(
            StackName=stackname
        )
        return True
    except:
        return False
