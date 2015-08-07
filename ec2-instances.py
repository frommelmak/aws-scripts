#!/usr/bin/env python
import boto3
import sys
import argparse


def list_instances(Filter):
   ec2 = boto3.resource('ec2')
   instances = ec2.instances.filter(Filters=Filter)
   print "Num Name                       Public IP        Type             Status"
   num = 1
   for i in instances:
      print "%-3d %-26s %-16s %-16s %-16s" % (num, i.tags[0]['Value'], i.public_ip_address, i.instance_type, i.state['Name'])
      num = num + 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name',
                        help="Filter result by name.")
    parser.add_argument('-t', '--type',
                        help="Filer result by type.")
    parser.add_argument('-s', '--status',
                        help="Filter result by status." )

    arg = parser.parse_args()

    # Default filter if no options are specified
    filter=[{
             'Name': 'tag-key',
             'Values': ['Name'],
           }]

    if arg.name:
        filter.append({'Name': 'tag-value', 'Values': ["*" + arg.name + "*"]})

    if arg.type:
        filter.append({'Name': 'instance-type', 'Values': ["*" + arg.type + "*"]})

    if arg.status:
        filter.append({'Name': 'instance-state-name', 'Values': ["*" + arg.status + "*"]})

    list_instances(filter)

if __name__ == '__main__':
    sys.exit(main())
