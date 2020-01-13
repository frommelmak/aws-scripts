#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
import argparse

def get_tag(ec2, id):
   instance = ec2.Instance(id)
   return instance.tags[0]['Value']

def list_elb(ec2):
    client = boto3.client('elb')
    response = client.describe_load_balancers()
    for elb in range(len(response.get('LoadBalancerDescriptions'))):
      load_balancer_name = response.get('LoadBalancerDescriptions')[elb].get('LoadBalancerName')
      instance_state = client.describe_instance_health(LoadBalancerName=load_balancer_name)
      print("%s" % load_balancer_name)
      for instance in range(len(response.get('LoadBalancerDescriptions')[elb].get('Instances'))):
         instance_id = instance_state.get('InstanceStates')[instance].get('InstanceId')
         print("  \_ %-20s (%s) Status: %s, Description: %s" % (
                                                               instance_id,
                                                               get_tag(ec2, instance_id),
                                                               instance_state.get('InstanceStates')[instance].get('State'),
                                                               instance_state.get('InstanceStates')[instance].get('Description')
                                                              ))


def main():
    parser = argparse.ArgumentParser(description='For every Elastic Load Balancer list the attached instances')
    arg = parser.parse_args()

    ec2 = boto3.resource('ec2')
    list_elb(ec2)

if __name__ == '__main__':
    sys.exit(main())
