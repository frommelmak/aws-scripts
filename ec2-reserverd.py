#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
import argparse
from datetime import datetime, timedelta

def list_reserved_instances(ec2, filters):
    client = boto3.client('ec2')
    response = client.describe_reserved_instances(Filters=filters)
    size = len(response.get('ReservedInstances'))
    columns_format="%-36s %-10s %-12s %-24s %-18s %-14s %-9s %-26s %-6s"
    print columns_format % ("Reserved Id", "Instances", "Type", "Product Description", "Scope", "Region", "Duration", "End", "Offering")
    for n in range(size):
        id=response.get('ReservedInstances')[n].get('ReservedInstancesId')
        count=response.get('ReservedInstances')[n].get('InstanceCount')
        type=response.get('ReservedInstances')[n].get('InstanceType')
        product=response.get('ReservedInstances')[n].get('ProductDescription')
        scope=response.get('ReservedInstances')[n].get('Scope')
        region=response.get('ReservedInstances')[n].get('AvailabilityZone')
        duration=response.get('ReservedInstances')[n].get('Duration')
        offering=response.get('ReservedInstances')[n].get('OfferingType')
        td=timedelta(seconds=int(duration))
        end=response.get('ReservedInstances')[n].get('End')
        print columns_format % (id, count, type, product, scope, region, td.days, end, offering)
        
def main():
    parser = argparse.ArgumentParser(description='Show active reserved EC2 instances')
    parser.add_argument('-s', '--state', action='store',
                        choices=['payment-pending', 'active', 'payment-failed', 'retired'],
                        help="Filer result by reservation state.")
    parser.add_argument('-t', '--type',
                        help="Filer result by instance type.")

    arg = parser.parse_args()

    filters=[]

    if arg.state:
        filters.append({'Name': 'state', 'Values': ["" + arg.state + ""]})

    if arg.type:
        filters.append({'Name': 'instance-type', 'Values': ["*" + arg.type + "*"]})

    ec2 = boto3.resource('ec2')
    list_reserved_instances(ec2, filters)

if __name__ == '__main__':
    sys.exit(main())
