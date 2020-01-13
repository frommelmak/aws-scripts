#!/usr/bin/env python

import boto3
import botocore
import sys
import argparse

def download_file(bucket, objectkey, filepath ):
    s3_client = boto3.client('s3')
    try:
      s3_client.download_file(bucket, objectkey, filepath)
      print("Requested file saved at: %s" % filepath)
    except botocore.exceptions.ClientError as e:
      if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
         print("Requested file: %s/%s (not found)" % (bucket, objectkey))
      else:
         print("Error Msg: %s" % e.response['Error']['Message'])

def main():
    parser = argparse.ArgumentParser(description='Donwload file from AWS S3')
    parser.add_argument('-b', '--bucket', required=True,
                        help="The bucket name.")
    parser.add_argument('-o', '--objectkey', required=True,
                        help="The host string used to build the new name")
    parser.add_argument('-f', '--filepath', required=True,
                        help="The filepath of the file to be saved" )

    arg = parser.parse_args()  

    download_file(arg.bucket, arg.objectkey, arg.filepath)

if __name__ == '__main__':
    sys.exit(main())
