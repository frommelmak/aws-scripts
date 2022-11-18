#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import argparse
import sys
from botocore.exceptions import ClientError
from rich.console import Console
from rich.table import Table

def list_security_groups(Filter, GroupIds, RegionName):
    
    ec2 = boto3.client('ec2', region_name=RegionName)
    table = Table()
    table.add_column("num", justify="right", style="cyan", no_wrap=True)
    table.add_column("SG ID", style="magenta")
    table.add_column("SG Name", style="green")
    table.add_column("Description", style="green")
    table.add_column("Inbound Rules", justify="right", style="green")
    table.add_column("Outbound Rules", justify="right", style="green")
    table.add_column("VPC", justify="right", style="green")

    num = 1

    try:
        sgs = ec2.describe_security_groups(Filters=Filter, GroupIds=GroupIds)
        for g in range(len(sgs.get('SecurityGroups'))):
            
            if len(sgs.get('SecurityGroups')[g].get('GroupName')) > 23:
                SGName = sgs.get('SecurityGroups')[g].get('GroupName')[ 0 : 23 ]+'...'
            else:
                SGName = sgs.get('SecurityGroups')[g].get('GroupName')
            
            table.add_row(
                str(num),
                str(sgs.get('SecurityGroups')[g].get('GroupId')),
                SGName,
                sgs.get('SecurityGroups')[g].get('Description'),
                str(len(sgs.get('SecurityGroups')[g].get('IpPermissions'))),
                str(len(sgs.get('SecurityGroups')[g].get('IpPermissionsEgress'))),
                sgs.get('SecurityGroups')[g].get('VpcId')                  
            )    

            num = num + 1
        console = Console()
        console.print(table)
    except ClientError as e:
        print(e)

def list_security_group(GroupId, RegionName):
    
    ec2 = boto3.client('ec2', region_name=RegionName)
    num = 1

    try:
        sgs = ec2.describe_security_groups(GroupIds=GroupId)
        print (sgs.get('SecurityGroups')[0].get('IpPermissions')[1])
        table = Table(title="Inbound Rules for "+sgs.get('SecurityGroups')[0].get('GroupName')+" Security Group")
        table.add_column("num", justify="right", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("SG Rule ID", style="green")
        table.add_column("IP Version", style="green")
        table.add_column("Type", justify="right", style="green")
        table.add_column("Protocol", justify="right", style="green")
        table.add_column("Port Range", justify="right", style="green")
        table.add_column("Source", justify="right", style="green")
        table.add_column("Descriptionx", style="green")
        for n in range(len(sgs.get('SecurityGroups')[0].get('IpPermissions'))):
            for ipv4 in range(len(sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('IpRanges'))):
                table.add_row(
                    str(num),
                    "name",
                    "rule id",
                    "IPv4",
                    "type",
                    sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('IpProtocol'),
                    str(sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('FromPort'))+"-"+str(sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('ToPort')),
                    sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('IpRanges')[ipv4].get('CidrIp'),
                    sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('IpRanges')[ipv4].get('Description')                  
                )
                num = num + 1
            for ipv6 in range(len(sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('Ipv6Ranges'))):
                table.add_row(
                    str(num),
                    "name",
                    "rule id",
                    "IPv6",
                    "type",
                    sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('IpProtocol'),
                    str(sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('FromPort')),
                    sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('Ipv6Ranges')[ipv6].get('CidrIp'),
                    sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('Ipv6Ranges')[ipv6].get('Description')                  
                )
                num = num + 1
            for uids in range(len(sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('UserIdGroupPairs'))):
                table.add_row(
                    str(num),
                    "name",
                    "rule id",
                    "-",
                    "type",
                    sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('IpProtocol'),
                    str(sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('FromPort')),
                    str(sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('UserIdGroupPairs')[uids].get('GroupId')),
                    sgs.get('SecurityGroups')[0].get('IpPermissions')[n].get('UserIdGroupPairs')[uids].get('Description')                  
                )
                num = num + 1

        console = Console()
        console.print(table)
    except ClientError as e:
        print(e)


def main():
    parser = argparse.ArgumentParser(description='Security Groups Management')
    parser.add_argument('-n', '--name',
                        help="Filter result by group name.")
    parser.add_argument('-l', '--gid_list',
                        nargs='+', type=str,
                        help="Do not filter the result. Provide a GroupIds list instead." )
    parser.add_argument('-r', '--region',
                        help="Specify an alternate region to override \
                              the one defined in the .aws/credentials file")
    parser.add_argument('--show',
                        help="Show inbound and outbound rules for the provided SG ID")

    arg = parser.parse_args()
    
    filter=[]
    GroupIds=[]

    if arg.name:
        filter.append({'Name': 'group-name', 'Values': ["*" + arg.name + "*"]})

    if arg.gid_list:
        GroupIds=arg.gid_list

    if arg.region: 
       client = boto3.client('ec2')
       regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
       if arg.region not in regions:
          sys.exit("ERROR: Please, choose a valid region.")

    if not arg.show:
        list_security_groups(filter, GroupIds, arg.region)
    else:
        list_security_group([arg.show], arg.region)

if __name__ == '__main__':
    sys.exit(main())
