#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='Set desired EC2 instance state')
    parser.add_argument('-s', '--state', action='store',
                        choices=['stop', 'start', 'reboot', 'terminate'],
                        help="Set the desired state for the instances provided")
    parser.add_argument('-l', '--id_list', required=True,
                        nargs='+', type=str,
                        help="InstanceIds list" )
    parser.add_argument('-r', '--region',
                        help="Specify an alternate region to override \
                              the one defined in the .aws/credentials file")

    arg = parser.parse_args()

    instances=[]

    if arg.region:
       client = boto3.client('ec2')
       regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
       if arg.region not in regions:
          sys.exit("ERROR: Please, choose a valid region.")

    if arg.id_list:
        instances=arg.id_list

    #region = 'us-west-1'
    print ('instances:' + str(instances))
    ec2 = boto3.client('ec2', region_name=arg.region)

    if arg.state == 'stop':
        ec2.stop_instances(InstanceIds=instances)
        print('stopped your instances: ' + str(instances))
    elif arg.state == 'start':
        ec2.start_instances(InstanceIds=instances)
        print('started your instances: ' + str(instances))
    elif arg.state == 'reboot':
        ec2.reboot_instances(InstanceIds=instances)
        print('rebooted your instances: ' + str(instances))
    elif arg.state == 'terminate':
        ec2.terminate_instances(InstanceIds=instances)
        print('terminated your instances: ' + str(instances))

if __name__ == '__main__':
    sys.exit(main())
