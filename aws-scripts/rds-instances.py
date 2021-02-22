#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
import argparse


def list_instances():
   client = boto3.client('rds')
   instances = client.describe_db_instances() 
   columns_format="%-3s %-20s %-60s %-14s %-7s %-8s %-8s %-12s %-11s %-11s %-12s"
   print(columns_format % ("num", "Identifier", "Endpoint Address", "Class", "Engine", "Version", "MultiAZ", "VPC", "Zone", "2ry Zone", "Status"))
   num = 1
   for n in range(len(instances.get('DBInstances'))):
      if instances.get('DBInstances')[n].get('DBSubnetGroup') is None:
          vpc_id = 'none'
      else:
          vpc_id = instances.get('DBInstances')[n].get('DBSubnetGroup').get('VpcId')
      print(columns_format % (
                               num,
                               instances.get('DBInstances')[n].get('DBInstanceIdentifier'),
                               instances.get('DBInstances')[n].get('Endpoint').get('Address'),
                               instances.get('DBInstances')[n].get('DBInstanceClass'),
                               instances.get('DBInstances')[n].get('Engine'),
                               instances.get('DBInstances')[n].get('EngineVersion'),
                               instances.get('DBInstances')[n].get('MultiAZ'),
                               vpc_id,
                               instances.get('DBInstances')[n].get('AvailabilityZone'),
                               instances.get('DBInstances')[n].get('SecondaryAvailabilityZone'),
                               instances.get('DBInstances')[n].get('DBInstanceStatus')
                             )) 
      num = num + 1

def main():
    parser = argparse.ArgumentParser(description='List all the RDS instances')
    arg = parser.parse_args()

    list_instances()

if __name__ == '__main__':
    sys.exit(main())
