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
      print response.get('LoadBalancerDescriptions')[elb].get('LoadBalancerName')
      for instance in range(len(response.get('LoadBalancerDescriptions')[elb].get('Instances'))):
         id = response.get('LoadBalancerDescriptions')[elb].get('Instances')[instance].get('InstanceId')
         instance = ec2.Instance(id)
         print u"  └── %s (%s)" % (id, instance.tags[0]['Value'])


def main():
    parser = argparse.ArgumentParser(description='For every Elastic Load Balancer list the attached instances')

    arg = parser.parse_args()
    list_elb()

if __name__ == '__main__':
    sys.exit(main())
