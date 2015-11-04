#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
import argparse

def list_elb():
   client = boto3.client('elb')
   response = client.describe_load_balancers()
   #response = client.describe_load_balancers(LoadBalancerNames=['apielb', ], PageSize=123)
   for elb in range(len(response.get('LoadBalancerDescriptions'))):
      print response.get('LoadBalancerDescriptions')[elb].get('LoadBalancerName')
      for instance in range(len(response.get('LoadBalancerDescriptions')[elb].get('Instances'))):
         print u"  └── %s" % response.get('LoadBalancerDescriptions')[elb].get('Instances')[instance].get('InstanceId')


def main():
    parser = argparse.ArgumentParser(description='For every Elastic Load Balancer list the attached instances')

    arg = parser.parse_args()
    list_elb()

if __name__ == '__main__':
    sys.exit(main())
