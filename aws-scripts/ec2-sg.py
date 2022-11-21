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
    table.add_column("num", justify="right", no_wrap=True)
    table.add_column("SG ID", style="cyan")
    table.add_column("SG Name", style="green")
    table.add_column("Description")
    table.add_column("Inbound Rules", justify="right", style="red")
    table.add_column("Outbound Rules", justify="right", style="red")
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

def list_security_group(Filter, RegionName):
    
    ec2 = boto3.client('ec2', region_name=RegionName)
    num = 1

    try:
        sgs = ec2.describe_security_group_rules(Filters=Filter)

        in_table = Table(title="Inbound Rules for "+Filter[0].get('Values')[0]+" Security Group")
        in_table.add_column("num", justify="right")
        in_table.add_column("SG Rule ID", style="cyan")
        in_table.add_column("IP Version", style="green")
        in_table.add_column("Protocol", justify="right", style="green")
        in_table.add_column("Port Range", justify="right", style="red")
        in_table.add_column("Source", justify="right", style="green")
        in_table.add_column("Description")
        
        out_table = Table(title="Outbound Rules for "+Filter[0].get('Values')[0]+" Security Group")
        out_table.add_column("num", justify="right")
        out_table.add_column("SG Rule ID", style="cyan")
        out_table.add_column("IP Version", style="green")
        out_table.add_column("Protocol", justify="right", style="green")
        out_table.add_column("Port Range", justify="right", style="red")
        out_table.add_column("Source", justify="right", style="green")
        out_table.add_column("Description")
                
        for n in range(len(sgs.get('SecurityGroupRules'))):
            
            if sgs.get('SecurityGroupRules')[n].get('ReferencedGroupInfo'):
                ip_version = "-"
                source = sgs.get('SecurityGroupRules')[n].get('ReferencedGroupInfo').get('GroupId')
                
            if sgs.get('SecurityGroupRules')[n].get('CidrIpv4'):
                ip_version = "IPv4"
                source = sgs.get('SecurityGroupRules')[n].get('CidrIpv4')
                
            if sgs.get('SecurityGroupRules')[n].get('CidrIpv6'):
                ip_version = "IPv6"
                source = sgs.get('SecurityGroupRules')[n].get('CidrIpv4')
                
            if sgs.get('SecurityGroupRules')[n].get('FromPort') == sgs.get('SecurityGroupRules')[n].get('ToPort'):
                if sgs.get('SecurityGroupRules')[n].get('FromPort') == -1:
                    port_range = 'all'
                else:
                    port_range = sgs.get('SecurityGroupRules')[n].get('FromPort')
            else:
                port_range = str(sgs.get('SecurityGroupRules')[n].get('FromPort'))+"-"+ str(sgs.get('SecurityGroupRules')[n].get('ToPort'))
                
            if sgs.get('SecurityGroupRules')[n].get('IpProtocol') == '-1':
                ip_protocol = 'all'
            else:
                ip_protocol = sgs.get('SecurityGroupRules')[n].get('IpProtocol')

            if sgs.get('SecurityGroupRules')[n].get('IsEgress'):
                out_table.add_row(
                    str(num),
                    sgs.get('SecurityGroupRules')[n].get('SecurityGroupRuleId'),
                    ip_version,
                    ip_protocol,
                    str(port_range),
                    source,
                    sgs.get('SecurityGroupRules')[n].get('Description')                  
                )
            else:
                in_table.add_row(
                    str(num),
                    sgs.get('SecurityGroupRules')[n].get('SecurityGroupRuleId'),
                    ip_version,
                    ip_protocol,
                    str(port_range),
                    source,
                    sgs.get('SecurityGroupRules')[n].get('Description')                  
                )                
            num = num + 1

        console = Console()
        console.print(in_table)
        console.print(out_table)
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
    parser.add_argument('-s','--show',
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
        filter =[]
        filter.append({'Name': 'group-id', 'Values': [arg.show]})
        list_security_group(filter, arg.region)

if __name__ == '__main__':
    sys.exit(main())
