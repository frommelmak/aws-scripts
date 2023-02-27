#!/usr/bin/env python
# -*- coding: utf-8 -*-
import botocore
import boto3
import argparse
import sys
import datetime
from dateutil.tz import tzlocal
from rich.console import Console
from rich.table import Table
import role

def list_target_groups(ec2):
    client = boto3.client('elbv2')
    response = client.describe_target_groups()
    table = Table()
    table.add_column("num", justify="right", no_wrap=True)
    table.add_column("Target Group Name", style="green")
    table.add_column("ARN", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Total Targets", style="white")
    table.add_column("Healthy", style="green")
    table.add_column("Unhealthy", style="red")
    for tg in range(len(response.get('TargetGroups'))):
        tg_name = response.get('TargetGroups')[tg].get('TargetGroupName')
        tg_arn = response.get('TargetGroups')[tg].get('TargetGroupArn')
        tg_type = response.get('TargetGroups')[tg].get('TargetType')
        targets=client.describe_target_health(TargetGroupArn=tg_arn)
        total=len(targets.get('TargetHealthDescriptions'))
        healthy=0
        for target in range(total):
            state=targets.get('TargetHealthDescriptions')[target].get('TargetHealth').get('State')
            if state == 'healthy':
                healthy+=1
        table.add_row(str(tg+1), tg_name, tg_arn, tg_type, str(total), str(healthy), str(total-healthy))
    console = Console()
    console.print(table)

def list_targets(ec2, arn_group):
    client = boto3.client('elbv2')
    targets=client.describe_target_health(TargetGroupArn=arn_group)
    total=len(targets.get('TargetHealthDescriptions'))
    healthy=0
    table = Table()
    table.add_column("num", justify="right", no_wrap=True)
    table.add_column("Target Id", style="green")
    table.add_column("Status", style="green")
    for target in range(total):
        target_id=targets.get('TargetHealthDescriptions')[target].get('Target').get('Id')
        state=targets.get('TargetHealthDescriptions')[target].get('TargetHealth').get('State')
        if state == 'healthy':
            state = "[green]"+state
        elif state == 'unhealthy':
            state = "[red]"+state
        else:
            state = "[orange1]"+state

        table.add_row(str(target+1), target_id, state)
    console = Console()
    console.print(table)

def register_target(ec2, arn_group, target_list):
    client = boto3.client('elbv2')
    try:
        response=client.register_targets(TargetGroupArn=arn_group, Targets=target_list)
    except botocore.exceptions.ClientError as error:
        print(error.response['Error']['Message'])

def unregister_target(ec2, arn_group, target_list):
    client = boto3.client('elbv2')
    try:
        response=client.deregister_targets(TargetGroupArn=arn_group, Targets=target_list)
    except botocore.exceptions.ClientError as error:
        print(error.response['Error']['Message'])


def main():
    parser = argparse.ArgumentParser(description='Shows a list of Target Grops.\
                        Also allows you to register/unregister targets in/from \
                        a provided Targer Group')
    parser.add_argument('-s', '--show',
                        help="Shows the target for the provided Target Group ARN")
    parser.add_argument('-a', '--action', action='store',
                        choices=['register', 'deregister', "details"],
                        help="Set the desired action.")
    parser.add_argument('--target_type', action='store',
                        choices=['instances', 'ip_address', 'lambda_function', 'alb'],
                        help="Set the desired state for the instances provided")
    parser.add_argument('--targets_id_list',
                        nargs='+', type=str,
                        help="Targets Id list" )
    parser.add_argument('--target_group_arn',
                        type=str,
                        help="Target Group ARN" )
    parser.add_argument('--role_arn', required=False, type=str,
                        help="If the script run on an EC2 instance with an IAM \
                              role attached, then the Security Token Service \
                              will provide a set of temporary credentials \
                              allowing the actions of the assumed role.\
                              With this method, no user credentials are \
                              required, just the Role ARN to be assumed." )
    parser.add_argument('-r', '--region',
                        help="Specify the region to override the one setted in \
                              the credentials file or if you are using \
                              --role_arn.")

    arg = parser.parse_args()

    if arg.role_arn:
      session = role.assumed_role_session(arg.role_arn)
      ec2 = session.client('ec2', region_name=arg.region)
    else:
      ec2 = boto3.client('ec2', region_name=arg.region)

    missing = 0
    if not arg.action:
        if arg.target_type:
            print('--target_type requires: -a or --action')
            missing += 1
        if arg.targets_id_list:
            print('--targets_id_list requires: -a or --action')
            missing += 1
        if arg.target_group_arn:
            print('--target_id_group requires: -a or --action')
            missing += 1

    if missing >= 1:
        sys.exit(1)

    if arg.action:
        if not arg.target_type:
            print('missing argument: --target_type')
        if not arg.targets_id_list:
            print('missing argument: --targets_id_list')
        if not arg.target_group_arn:
            print('missing argument: --target_group_arn')
        if arg.targets_id_list and arg.target_group_arn and arg.target_type:
            if arg.target_type != 'instances':
                print('Non-instance types are not yet supported!')
                sys.exit(1)
            targets=[]
            target={}
            for id in arg.targets_id_list:
                target={'Id': id}
                targets.append(target)
            if arg.action == 'register':
                register_target(ec2, arg.target_group_arn, targets)
            elif arg.action == 'unregister':
                register_target(ec2, arg.target_group_arn, targets)

    elif arg.show:
        session = boto3.session.Session()
        region = session.region_name
        ec2 = boto3.resource('ec2')
        list_targets(ec2, arg.show)
    else:
        session = boto3.session.Session()
        region = session.region_name
        ec2 = boto3.resource('ec2')
        list_target_groups(ec2)



if __name__ == '__main__':
    sys.exit(main())
