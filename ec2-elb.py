#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
import argparse

def list_elb():
   client = boto3.client('elb')
   response = client.describe_load_balancers()
   ec2 = boto3.resource('ec2')
   for elb in range(len(response.get('LoadBalancerDescriptions'))):
      load_balancer_name = response.get('LoadBalancerDescriptions')[elb].get('LoadBalancerName')
      print u"%s" % load_balancer_name
      for instance in range(len(response.get('LoadBalancerDescriptions')[elb].get('Instances'))):
         id = response.get('LoadBalancerDescriptions')[elb].get('Instances')[instance].get('InstanceId')
         instance_id = ec2.Instance(id)
         instance_state = client.describe_instance_health(LoadBalancerName=load_balancer_name)
         print u"  └── %s (%s) Status: %s, Description: %s" % (
                                                               id, 
                                                               instance_id.tags[0]['Value'],
                                                               instance_state.get('InstanceStates')[instance].get('State'),
                                                               instance_state.get('InstanceStates')[instance].get('Description')
                                                              )


def main():
    parser = argparse.ArgumentParser(description='For every Elastic Load Balancer list the attached instances')

    arg = parser.parse_args()
    list_elb()

if __name__ == '__main__':
    sys.exit(main())
