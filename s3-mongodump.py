#!/usr/bin/env python
import boto3
import sys
import argparse
import subprocess
import shutil
import os
from datetime import datetime

def dump(host, database, username, password):

    if username and password:
        auth_str= "--username %s --password %s" % (username, password)
    else:
        auth_str=""

    if database:
        db_str="--db %s" % (database)
    else:
        db_str=""

    mongodump_cmd="mongodump --host %s %s %s" % (host,auth_str,db_str)
    print mongodump_cmd 
    mongodump_output = subprocess.check_output(mongodump_cmd, shell=True)
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
    parser.add_argument('-n', '--number', type=int, default=7,
                        help="Number of copies to retain in the S3 bucket")
    parser.add_argument('-b', '--bucket', required=True,
                        help="Amazon s3 bucket." )
    parser.add_argument('-P', '--prefix',
                        help="For grouped objects aka s3 folders, provide the prefix key")

    arg = parser.parse_args()

    if arg.user and not arg.password:
           parser.error("You provided a user but not a password")

    if arg.password and not arg.user:
           parser.error("You provided a password but not a user")
    
    # mongodump
    dump(arg.host, arg.database, arg.user, arg.password)

    # List and get the number of files in the bucket
    num_files=0
    s3 = boto3.resource('s3')
    if arg.prefix:
        objects=s3.Bucket(name=arg.bucket).objects.filter(Prefix=arg.prefix)
        num_files=-1
    else:
        objects=s3.Bucket(name=arg.bucket).objects.filter()
        num_files=0

    print "Filelist on the S3 bucket:"
    for object in objects:
        print (object.key)
        num_files=num_files + 1
    
    # create new tarball
    num_files=num_files+1
    print "Creating the tarball:"
    tarball_name="dump-%s.tar.gz" % datetime.strftime(datetime.now(),'%Y-%m-%d-%H%M%S') 
    tarball_cmd="tar -czvf %s dump" % (tarball_name)
    tarball_output = subprocess.check_output(tarball_cmd, shell=True)
    print tarball_output

    # remove dumped files
    print "Removing temporary dump files..."
    shutil.rmtree('dump')

    # upload the new tarball to s3
    remote_file="%s/%s" % (arg.prefix,tarball_name)
    print "Uploading %s to Amazon S3..." % tarball_name
    s3.Object(arg.bucket, remote_file).put(Body=open(tarball_name, 'rb'))

    # remove temprary tarball
    print "Removing temporary local tarball..."
    os.remove(tarball_name)

    # remove expired dumps from s3

if __name__ == '__main__':
    sys.exit(main())
