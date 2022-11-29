#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import argparse
import sys
from botocore.exceptions import ClientError
from rich.console import Console
from rich.table import Table
from requests import get
import random
import datetime

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
            ip_ranges =[] 
            ipv6_ranges = []
            prefix_list_ids = []
            user_id_group_pairs = []
            for r in range(len(sgs.get('SecurityGroups')[g].get('IpPermissions'))):
                ip_ranges = sgs.get('SecurityGroups')[g].get('IpPermissions')[r].get('IpRanges')
                ipv6_ranges = sgs.get('SecurityGroups')[g].get('IpPermissions')[r].get('Ipv6Ranges')
                prefix_list_ids = sgs.get('SecurityGroups')[g].get('IpPermissions')[r].get('PrefixListIds')
                user_id_group_pairs = sgs.get('SecurityGroups')[g].get('IpPermissions')[r].get('UserIdGroupPairs')
            inbound_rules_count = len(ip_ranges) + len(ipv6_ranges) + len (prefix_list_ids) + len(user_id_group_pairs)
            for r in range(len(sgs.get('SecurityGroups')[g].get('IpPermissionsEgress'))):
                ip_ranges = sgs.get('SecurityGroups')[g].get('IpPermissionsEgress')[r].get('IpRanges')
                ipv6_ranges = sgs.get('SecurityGroups')[g].get('IpPermissionsEgress')[r].get('Ipv6Ranges')
                prefix_list_ids = sgs.get('SecurityGroups')[g].get('IpPermissionsEgress')[r].get('PrefixListIds')
                user_id_group_pairs = sgs.get('SecurityGroups')[g].get('IpPermissionsEgress')[r].get('UserIdGroupPairs')
            outbound_rules_count = len(ip_ranges) + len(ipv6_ranges) + len (prefix_list_ids) + len(user_id_group_pairs)
            table.add_row(
                str(num),
                str(sgs.get('SecurityGroups')[g].get('GroupId')),
                SGName,
                sgs.get('SecurityGroups')[g].get('Description'),
                str(inbound_rules_count),
                str(outbound_rules_count),
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
    parser.add_argument('--allow_my_public_ip',
                        help="Modify the SSH inbound rule with your current public IP \
                              address inside the provided Security Group ID.")
    parser.add_argument('--security_group_rule_id',
                        help="Modify the SSH inbound rule with your current public IP \
                             address inside the provided Security Group Rule ID")
    parser.add_argument('--description',
                        default="",
                        help="Allows you to append a string to the rule description field")

    arg = parser.parse_args()
    
    filter=[]
    GroupIds=[]

    if arg.allow_my_public_ip and not arg.security_group_rule_id:
        print("The argument allow_my_public_ip requires the argument security_group_rule_id.")
        sys.exit(1)

    if arg.allow_my_public_ip:
        ec2 = boto3.client('ec2')
        ip=None
        ip_services=[
                     "https://api.ipify.org",
                     "https://ifconfig.me",
                     "https://api.my-ip.io/ip",
                     "http://myexternalip.com/raw",
                     "http://ipwho.is/&fields=ip&output=csv"
                     ]
        random.shuffle(ip_services)
        for url in ip_services:
            try:
                ip = get(url).content.decode('utf8')
                break
            except:
                print("%s fail. Trying next..." % url)
        if ip is None:
            print("Public IP address not found using any services")
            sys.exit(1)
        else:
            now = datetime.datetime.now()
            try:
                data = ec2.modify_security_group_rules(
                GroupId=arg.allow_my_public_ip,
                SecurityGroupRules=[
                        {
                            'SecurityGroupRuleId': arg.security_group_rule_id,
                            'SecurityGroupRule': {
                                'IpProtocol': 'tcp',
                                'FromPort': 22,
                                'ToPort': 22,
                                'CidrIpv4': ip+'/32',
                                'Description': '('+arg.description+') '+now.strftime("%Y-%m-%d %H:%M:%S")+' by ec2-sg.py from aws-scripts'
                            }
                        },
                ])
                if data:
                    rule_table = Table(title="Inbound Rule updated on the "+arg.allow_my_public_ip+" Security Group")
                    rule_table.add_column("SG Rule ID", style="cyan")
                    rule_table.add_column("IP Version", style="green")
                    rule_table.add_column("Type", style="green")
                    rule_table.add_column("Protocol", justify="right", style="green")
                    rule_table.add_column("Port Range", justify="right", style="green")
                    rule_table.add_column("Source", justify="right", style="green")
                    rule_table.add_column("Description", justify="right", style="green")
                    rule_table.add_row(
                        arg.security_group_rule_id,
                        "IPv4",
                        "SSH",
                        "TCP",
                        "[red]22",
                        "[red]"+ip+"/32",
                        "[white]("+arg.description+") "+now.strftime("%Y-%m-%d %H:%M:%S")+" by ec2-sg.py from aws-scripts"
                    )
                    console = Console()
                    console.print(rule_table)
                    sys.exit(0)
                else:
                    print("an error occurred!")
            except ClientError as e:
                print(e)
                sys.exit(0)
        
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
