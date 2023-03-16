#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
import argparse
from rich.console import Console
from rich.table import Table

def list_volumes(Filter):
   ec2 = boto3.resource('ec2')
   # Getting all the instances ids and his tag Name
   instances_lst=[]
   instances = ec2.instances.all()
   for i in instances:
        try:
           if i.tags is not None:
               name = next((item for item in i.tags if item["Key"] == "Name"))
           else:
               name['Value'] = ''
        except StopIteration:
               name['Value'] = ''
        item={'id': i.id, 'name': name['Value'],}
        instances_lst.append(item)
   
   
   volumes = ec2.volumes.filter(Filters=Filter)
   table = Table()
   table.add_column("num", justify="right", no_wrap=True)
   table.add_column("Name", style="green")
   table.add_column("Size", style="red")
   table.add_column("device", style="green")
   table.add_column("Volume ID", justify="right", style="cyan")
   table.add_column("Instance ID", justify="right", style="cyan")
   table.add_column("Instance Tag Name", justify="right", style="green")
   table.add_column("Type", style="green")
   table.add_column("IOPS", style="red")
   table.add_column("Zone", style="green")
   table.add_column("Status", style="green")
   num = 1
   vols = [] 
   name = {}  
   for i in volumes:
      try:
         if i.tags is not None:
           name = next((item for item in i.tags if item["Key"] == "Name"))
         else:
           name['Value'] = ''
      except StopIteration:
           name['Value'] = ''
      
      if len(i.attachments) == 0:
          device = ''
          instance_id = ''
      elif len(i.attachments) == 1:
          device = i.attachments[0]['Device']
          instance_id = i.attachments[0]['InstanceId']
      else:
          # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-volumes-multi.html
          device = 'Multi-Attach'
          instance_id = 'Multi-Attach'
      
      ec2_attached = next((instance for instance in instances_lst if instance["id"] == instance_id), {'id': instance_id, 'name':''}) 
      #print(tag_name['name'])      
      table.add_row(
        str(num),
        name['Value'], 
        str(i.size) + " GB",
        device,
        i.volume_id,
        instance_id,
        ec2_attached['name'],
        i.volume_type,
        str(i.iops),
        i.availability_zone,
        i.state
      )
      num = num + 1
   console = Console()
   console.print(table)


def main():
    parser = argparse.ArgumentParser(description='List all the Elastic Block Storage volumes')
    parser.add_argument('-n', '--name',
                        help="Filter result by name.")
    parser.add_argument('-t', '--type',
                        choices=['gp3', 'gp2', 'io1', 'st1', 'sc1', 'standard'],
                        help="Filer result by type.")
    parser.add_argument('-s', '--status',
                        choices=['creating','available','in-use','deleting','deleted','error'],
                        help="Filter result by status." )
    arg = parser.parse_args()

    # Default filter if no options are specified
    filter=[]
    InstanceIds=[]
    
    if arg.name:
        filter.append({'Name': 'tag-value', 'Values': ["*" + arg.name + "*"]})

    if arg.type:
        filter.append({'Name': 'volume-type', 'Values': ["*" + arg.type + "*"]})

    if arg.status:
        filter.append({'Name': 'status', 'Values': ["*" + arg.status + "*"]})

    vols=list_volumes(filter)

if __name__ == '__main__':
    sys.exit(main())
