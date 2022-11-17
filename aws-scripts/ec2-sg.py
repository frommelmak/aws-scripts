#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import argparse
import sys

from botocore.exceptions import ClientError

def list_security_groups(Filter, GroupIds, RegionName):
    
    ec2 = boto3.client('ec2', region_name=RegionName)
    columns_format="%-3s %-21s %-26s %-62s %-15s %-15s %-60s"
    print(columns_format % ("num", "SG ID", "SG Name", "Description", "Inbound Rules", "Outbound Rules", "VPC"))
    num = 1

    try:
        sgs = ec2.describe_security_groups(Filters=Filter, GroupIds=GroupIds)
        for g in range(len(sgs.get('SecurityGroups'))):
            
            if len(sgs.get('SecurityGroups')[g].get('GroupName')) > 23:
                SGName = sgs.get('SecurityGroups')[g].get('GroupName')[ 0 : 23 ]+'...'
            else:
                SGName = sgs.get('SecurityGroups')[g].get('GroupName')
                
            if len(sgs.get('SecurityGroups')[g].get('Description')) > 59:
                SGDescription = sgs.get('SecurityGroups')[g].get('Description')[ 0 : 59 ]+'...'
            else:
                SGDescription = sgs.get('SecurityGroups')[g].get('Description')

            print(columns_format % (
                                    num,
                                    sgs.get('SecurityGroups')[g].get('GroupId'),
                                    SGName,
                                    SGDescription,
                                    len(sgs.get('SecurityGroups')[g].get('IpPermissions')),
                                    len(sgs.get('SecurityGroups')[g].get('IpPermissionsEgress')),
                                    sgs.get('SecurityGroups')[g].get('VpcId')
                                   )) 

            num = num + 1
    except ClientError as e:
        print(e)

def main():
    parser = argparse.ArgumentParser(description='Security Groups Management')
    parser.add_argument('-n', '--name',
                        help="Filter result by group name.")
    parser.add_argument('-l', '--gid_list',
                        nargs='+', type=str,
                        help="Do not filter the result. Provide a InstanceIds list instead." )
    parser.add_argument('-r', '--region',
                        help="Specify an alternate region to override \
                              the one defined in the .aws/credentials file")
    parser.add_argument('--show-rules',
                        help="Show inbound and outbound rules for every result")

    arg = parser.parse_args()
    
    filter=[]

    if arg.name:
        filter.append({'Name': 'group-name', 'Values': ["*" + arg.name + "*"]})

    if arg.gid_list:
        GroupIds=arg.gid_list

    if arg.region: 
       client = boto3.client('ec2')
       regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
       if arg.region not in regions:
          sys.exit("ERROR: Please, choose a valid region.")

    list_security_groups(filter, GroupIds, arg.region)

if __name__ == '__main__':
    sys.exit(main())
