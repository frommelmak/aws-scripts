#!/usr/bin/env python
import boto3
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='A tool to make mongodb backups on Amazon s3')
    parser.add_argument('-u', '--user',
                        help="Mongodb user (optional)")
    parser.add_argument('-p', '--password',
                        help="Mongodb password (optional)")
    parser.add_argument('-t', '--type',
                        help="Mongodb password (optional)")
    parser.add_argument('-H', '--host', default="localhost:27017",
                        help="Mongodb host." )
    parser.add_argument('-d', '--database',
                        help="The database to backup (all if not provided)")
    parser.add_argument('-o', '--out', default="/tmp",
                        help="Specifies the directory for the dumped databases")
    parser.add_argument('-n', '--number', type=int, default=7,
                        help="Number of copies to retain")
    parser.add_argument('-b', '--bucket', required=True,
                        help="Amazon s3 bucket." )

    arg = parser.parse_args()


if __name__ == '__main__':
    sys.exit(main())
