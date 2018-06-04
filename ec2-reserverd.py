#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
import argparse

def list_reserved_instances(ec2):
    client = boto3.client('ec2')
    filters = []
    filters.append({'Name': 'state', 'Values': ['active']})
    response = client.describe_reserved_instances(Filters=filters)
    size = len(response.get('ReservedInstances'))
    columns_format="%-5s %-36s %-10s %-6s"
    print columns_format % ("num", "Reserved Id", "Instances", "Type")
    for n in range(size):
        id=response.get('ReservedInstances')[n].get('ReservedInstancesId')
        count=response.get('ReservedInstances')[n].get('InstanceCount')
        type=response.get('ReservedInstances')[n].get('InstanceType')
        print columns_format % (n, id, count, type)
        
def main():
    parser = argparse.ArgumentParser(description='Show active reserved EC2 instances')
    arg = parser.parse_args()

    ec2 = boto3.resource('ec2')
    list_reserved_instances(ec2)
    

if __name__ == '__main__':
    sys.exit(main())
