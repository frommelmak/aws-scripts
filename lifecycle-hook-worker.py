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

def main():
    parser = argparse.ArgumentParser(description='SQS Lifecycle hook consumer and trigger')
    parser.add_argument('-q', '--queue', required=True,
                        help="Queue resource.")
    parser.add_argument('-e', '--execute', required=True,
                        help="The filepath of the triggered script")

    arg = parser.parse_args()  

    sqs_consumer(arg.queue, arg.execute)

if __name__ == '__main__':
    sys.exit(main())
