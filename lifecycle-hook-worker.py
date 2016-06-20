#!/usr/bin/env python

import boto3
import sys
import argparse

def sqs_consumer(qname, execute ):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=qname)
    print(queue.url)
    client = boto3.client('sqs')
    message=client.receive_message(QueueUrl=queue.url)
    print(message)
    print("ID:%s") % message['ResponseMetadata']['RequestId']

def complete_lifecycle(lhn,asgn,lat):
    client = boto3.client('autoscaling')
    response = client.complete_lifecycle_action(
       LifecycleHookName=lhn,
       AutoScalingGroupName=asgn,
       LifecycleActionToken=lat,
       LivecycleActionResult='CONTINUE',
       InstanceID=''
    )

def main():
    parser = argparse.ArgumentParser(description='SQS Lifecycle hook consumer and trigger')
    parser.add_argument('-q', '--queue', required=True,
                        help="Queue resource.")
    parser.add_argument('-s', '--state', action='store', choices=['LAUNCHING','TERMINATING'], required=True,
                        help='Indicates if the consumer is waiting for LAUNCHING or TERMINATING state')
    parser.add_argument('-g', '--group', required=True,
                        help='Auto Scaling Group Name')
    parser.add_argument('-H', '--hookName', required=True,
                        help='Life Cycle Hook Name')
    parser.add_argument('-e', '--execute', required=True,
                        help="The filepath of the triggered script")

    arg = parser.parse_args()  

    sqs_consumer(arg.queue, arg.execute)

if __name__ == '__main__':
    sys.exit(main())
