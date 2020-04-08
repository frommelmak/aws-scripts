#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
import argparse

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
   columns_format="%-3s %-26s %6s GB  %-16s %-22s %-20s %-24s %-10s %-11s %-12s %-16s"
   print(columns_format % ("num", "Name", "Size", "device", "Volume ID", "Instance ID", "Instance Tag Name", "Type", "IOPS", "Zone", "Status"))
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
      print(columns_format % (
                               num,
                               name['Value'], 
                               i.size,
                               device,
                               i.volume_id,
                               instance_id,
                               ec2_attached['name'],
                               i.volume_type,
                               i.iops,
                               i.availability_zone,
                               i.state
                             ))
      num = num + 1

def main():
    parser = argparse.ArgumentParser(description='List all the Elastic Block Storage volumes')
    parser.add_argument('-n', '--name',
                        help="Filter result by name.")
    parser.add_argument('-t', '--type',
                        choices=['gp2', 'io1', 'st1', 'sc1', 'standard'],
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
