#!/usr/bin/env python
# -*- coding: utf-8 -*-
import botocore
import boto3
import argparse
import sys
import datetime
from dateutil.tz import tzlocal
import role

def main():
    parser = argparse.ArgumentParser(description='Set desired EC2 instance state')
    parser.add_argument('-s', '--state', action='store',
                        choices=['stop', 'start', 'reboot', 'terminate'],
                        help="Set the desired state for the instances provided")
    parser.add_argument('-l', '--id_list', required=True,
                        nargs='+', type=str,
                        help="InstanceIds list" )
    parser.add_argument('--role_arn', required=False, type=str,
                        help="If the script run on an EC2 instance with an IAM \
                              role attached, then the Security Token Service \
                              will provide a set of temporary credentials \
                              allowing the actions of the assumed role.\
                              With this method, no user credentials are \
                              required, just the Role ARN to be assumed." )
    parser.add_argument('-r', '--region', required=True,
                        help="Specify the region. This flag is required")

    arg = parser.parse_args()

    instances=[]

    if arg.id_list:
        instances=arg.id_list

    print ('instances:' + str(instances))

    if arg.role_arn:
      session = role.assumed_role_session(arg.role_arn)
      ec2 = session.client('ec2', region_name=arg.region)
    else:
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
