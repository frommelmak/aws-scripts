#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
import argparse
from rich.console import Console
from rich.table import Table

def list_instances():
   client = boto3.client('rds')
   instances = client.describe_db_instances() 
   num = 1
   table = Table()
   table.add_column("num", justify="right", no_wrap=True)
   table.add_column("Identifier", style="green")
   table.add_column("Endpoint Address", style="cyan")
   table.add_column("Class", justify="right", style="green")
   table.add_column("Engine", justify="right", style="green")
   table.add_column("Version", justify="right", style="red")
   table.add_column("MultiAZ", style="cyan")
   table.add_column("VPC", style="cyan")
   table.add_column("Zone", style="cyan")
   table.add_column("2ry Zone", style="cyan")
   table.add_column("Status")

   for n in range(len(instances.get('DBInstances'))):
      if instances.get('DBInstances')[n].get('DBSubnetGroup') is None:
          vpc_id = 'none'
      else:
          vpc_id = instances.get('DBInstances')[n].get('DBSubnetGroup').get('VpcId')
      if instances.get('DBInstances')[n].get('DBInstanceStatus') == 'stopped':
          table.add_row(
              str(num),
              instances.get('DBInstances')[n].get('DBInstanceIdentifier'),
              instances.get('DBInstances')[n].get('Endpoint').get('Address'),
              instances.get('DBInstances')[n].get('DBInstanceClass'),
              instances.get('DBInstances')[n].get('Engine'),
              instances.get('DBInstances')[n].get('EngineVersion'),
              str(instances.get('DBInstances')[n].get('MultiAZ')),
              vpc_id,
              instances.get('DBInstances')[n].get('AvailabilityZone'),
              instances.get('DBInstances')[n].get('SecondaryAvailabilityZone'),
              instances.get('DBInstances')[n].get('DBInstanceStatus'),
              style='italic grey42'
          )
      else:
          table.add_row(
              str(num),
              instances.get('DBInstances')[n].get('DBInstanceIdentifier'),
              instances.get('DBInstances')[n].get('Endpoint').get('Address'),
              instances.get('DBInstances')[n].get('DBInstanceClass'),
              instances.get('DBInstances')[n].get('Engine'),
              instances.get('DBInstances')[n].get('EngineVersion'),
              str(instances.get('DBInstances')[n].get('MultiAZ')),
              vpc_id,
              instances.get('DBInstances')[n].get('AvailabilityZone'),
              instances.get('DBInstances')[n].get('SecondaryAvailabilityZone'),
              instances.get('DBInstances')[n].get('DBInstanceStatus')
          )
      num = num + 1
   console = Console()
   console.print(table)

def main():
    parser = argparse.ArgumentParser(description='List all the RDS instances')
    arg = parser.parse_args()

    list_instances()

if __name__ == '__main__':
    sys.exit(main())
