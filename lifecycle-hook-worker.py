#!/usr/bin/env python

import boto3
import sys
import argparse
import ast
import urllib2

def sqs_consumer(qname):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=qname)
    client = boto3.client('sqs')
    message = client.receive_message(QueueUrl=queue.url, MaxNumberOfMessages=1, WaitTimeSeconds=10)
    if message.get('Messages'):
       m = message.get('Messages')[0]
       body = ast.literal_eval(m['Body'])
       receipt_handle = m['ReceiptHandle']
       response = client.delete_message(QueueUrl=queue.url, ReceiptHandle=receipt_handle)
    else:
       body = {'timeout': True, 'Event': False}
    return(body)

def get_ec2instanceid():
    # curl http://169.254.169.254/latest/meta-data/instance-id
    response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id')
    instanceid = response.read()
    return instanceid

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

    if arg.state == "LAUNCHING":
       state = "autoscaling:EC2_INSTANCE_TERMINATING"
    elif arg.state == "TERMINATING":
       state = "autoscaling:EC2_INSTANCE_LAUNCHING"
   
    ec2instanceid = get_ec2instanceid()
    
    while 1:
       sqs_msg = sqs_consumer(arg.queue)
       if sqs_msg['Event'] == "autoscaling:TEST_NOTIFICATION":
          print ("Tests message consumed")
       elif sqs_msg['timeout']:
          print ("There are no messages in the queue. Trying again")         
       elif (sqs_msg['Event'] == state) and (sqs_msg['EC2InstanceId'] == ec2instanceid):
          print "%s hook message received" % arg.state
          print "Calling to exec filepath"

if __name__ == '__main__':
    sys.exit(main())
