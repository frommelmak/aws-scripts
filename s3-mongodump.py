#!/usr/bin/env python
import boto3
import sys
import argparse
import subprocess

def dump(host, database, out, username, password):

    if username and password:
        auth_str= "--username %s --password %s" % (username, password)
    else:
        auth_str=""

    if database:
        db_str="--db %s" % (database)
    else:
        db_str=""

    command="mongodump --host %s %s %s --out %s" % (host,auth_str,db_str,out)
    print command
    mongodump_output = subprocess(command, shell=True)
    print mongodump_output

def main():
    parser = argparse.ArgumentParser(description='A tool to make mongodb backups on Amazon s3')
    parser.add_argument('-u', '--user',
                        help="Mongodb user (optional)")
    parser.add_argument('-p', '--password',
                        help="Mongodb password (optional)")
    parser.add_argument('-H', '--host', default="localhost:27017",
                        help="Mongodb host: <hostname>:<port>." )
    parser.add_argument('-d', '--database',
                        help="The database to backup (all if not provided)")
    parser.add_argument('-o', '--out', default="/tmp",
                        help="Specifies the directory for the dumped databases")
    parser.add_argument('-n', '--number', type=int, default=7,
                        help="Number of copies to retain")
    parser.add_argument('-b', '--bucket', required=True,
                        help="Amazon s3 bucket." )

    arg = parser.parse_args()

    if arg.user and not arg.password:
           parser.error("You provided a user but not a password")

    if arg.password and not arg.user:
           parser.error("You provided a password but not a user")

    dump(arg.host, arg.database, arg.out, arg.user, arg.password)

if __name__ == '__main__':
    sys.exit(main())
