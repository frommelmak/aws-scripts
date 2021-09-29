#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import botocore
import sys
import argparse
import subprocess
import shutil
import os
from datetime import datetime
import operator
import distutils.spawn
from pymongo import MongoClient
from pymongo import errors

def fsync(action, host, username, password):
    client = MongoClient(host)
    db = client['admin']
    
    if action == 'lock':
        # lock    
        if username and password:
            try:
                db.authenticate(username, password)
                print("[+] Database connected!")
                try:
                   lock = db.command("fsync", lock=True)["info"]
                except Exception as e:
                   raise e
            except Exception as e:
                print("[+] Database connection error!")
                raise e
        else:
            try:
               lock = db.command("fsync", lock=True)["info"]
            except Exception as e:
               raise e
    elif action == 'unlock':
        # unlock
        if username and password:
            try:
                db.authenticate(username, password)
                print("[+] Database connected!")
                try:
                   lock = db.command("fsyncUnlock")["info"]
                except Exception as e:
                   raise e
            except Exception as e:
                print("[+] Database connection error!")
                raise e
        else:
            try:
               lock = db.command("fsyncUnlock")["info"]
            except Exception as e:
               raise e
    
    return lock

def create_snapshot(RegionName, volumes_dict):

    dtime = datetime.now()
    client = boto3.client('ec2', region_name=RegionName)
    successful_snapshots = dict()
    # iterate through each item in volumes_dict and use key as description of snapshot
    for snapshot in volumes_dict:
        try:
            response = client.create_snapshot(
                Description= "Crated by aws-scripts/mongodb_backup.py ",
                VolumeId= volumes_dict[snapshot],
                TagSpecifications=[
                    {
                        'ResourceType': 'snapshot',
                        'Tags': [
                            {
                                'Key': 'aws-scripts:mongodb_backup.py:managed',
                                'Value': 'true'
                            },
                            {
                                'Key': 'Name',
                                'Value': dtime
                            },
                        ]
                    },
                ],
                DryRun= False
            )
            # response is a dictionary containing ResponseMetadata and SnapshotId
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            snapshot_id = response['SnapshotId']
            # check if status_code was 200 or not to ensure the snapshot was created successfully
            if status_code == 200:
                successful_snapshots[snapshot] = snapshot_id
            else:
                print("status code: %s" % status_code)
        except Exception as e:
            exception_message = "There was error in creating snapshot " + snapshot + " with volume id "+volumes_dict[snapshot]+" and error is: \n"\
                                + str(e)
    # print the snapshots which were created successfully
    if len(successful_snapshots) == 1:
       print("  Snapshots: %s " % successful_snapshots['data'])
       snap_ids=[successful_snapshots['data']]

    if len(successful_snapshots) == 2:
       print("  Snapshots: %s, %s " % (successful_snapshots['data'],successful_snapshots['journal']))
       snap_ids=[successful_snapshots['data'], successful_snapshots['journal']]
    
    return snap_ids

def dump(host, database, collection, exclude_collection, username, password, out):

    if username and password:
        auth_str= "--username %s --password %s" % (username, password)
    else:
        auth_str=""

    if database:
        db_str="--db %s" % (database)
        if exclude_collection:
            db_str="--db %s --excludeCollection %s" % (database, exclude_collection)
        if collection:
            db_str="--db %s --collection %s" % (database, collection)
    else:
        db_str=""

    mongodump_cmd="mongodump --host %s -o %s %s %s" % (host,out,auth_str,db_str)
    print(mongodump_cmd)
    mongodump_output = subprocess.check_output(mongodump_cmd, shell=True)
    print(mongodump_output)

def main():
    parser = argparse.ArgumentParser(description='A tool to make mongodb backups on Amazon')
    parser.add_argument('-m', '--method',
                        help="Backup method. Dump if none is provided",
                        choices=['dump', 'snapshot'],
                        default="dump")
    parser.add_argument('-u', '--user',
                        help="Mongodb user (optional)")
    parser.add_argument('-p', '--password',
                        help="Mongodb password (optional)")
    parser.add_argument('-H', '--host', default="localhost:27017",
                        help="Mongodb host: <hostname>:<port>. By default: localhost:27017" )
    parser.add_argument('-d', '--database',
                        help="For the dump method: The database to backup (all if not provided)")
    parser.add_argument('-c', '--collection',
                        help="For the dump method: The collection to backup. Requires '-d' option")
    parser.add_argument('-e', '--exclude_collection',
                        help="For the dump method: The collection to exclude from backup. Requires '-d' option")
    parser.add_argument('-o', '--out', default='dump',
                        help="For the dump method: The output directory for dumped files")
    parser.add_argument('-n', '--number', type=int, default=7,
                        help="Number of copies to retain")
    parser.add_argument('-b', '--bucket',
                        help="For the dump method: Amazon s3 bucket." )
    parser.add_argument('-P', '--prefix',
                        help="For the dump method: For grouped objects aka s3 folders, provide the prefix key")
    parser.add_argument('-v', '--volume_id',
                        nargs='+', type=str,
                        help="For the snapshot method: Provide the data and journal volume_id list to snapshot: If data and journal resides in a separate volumes, both volumes are required.")
    parser.add_argument('--no_journal',
                        action='store_true',
                        help="For the snapshot method: If pressent,  the instance is either running without journaling or has the journal files on a separate volume, you must flush all writes to disk and lock the database to prevent writes during the backup process.")
    parser.add_argument('-r', '--region',
                        help="Specify an alternate region to override \
                              the one defined in the .aws/credentials file")


    arg = parser.parse_args()

    if arg.user and not arg.password:
           parser.error("You provided a user but not a password")

    if arg.password and not arg.user:
           parser.error("You provided a password but not a user")

    if arg.prefix is not None and arg.prefix[-1:] == "/":
       arg.prefix="%s" % arg.prefix[:-1]

    if arg.exclude_collection and not arg.database:
       parser.error("--exclude_collection requires --database")
    
    if arg.collection and not arg.database:
       parser.error("--collection requires --database")

    if arg.region:
       client = boto3.client('ec2')
       regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
       if arg.region not in regions:
          sys.exit("ERROR: Please, choose a valid region.")

    if arg.method == "dump":
        print("Method: dump")
        mongodump_path=distutils.spawn.find_executable("mongodump")
        if mongodump_path is not None:
            print("mongodump path: %s" % mongodump_path)
        else:
            print("mongodump path: not found!")
            sys.exit(1)
        # mongodump
        dump(arg.host, arg.database, arg.collection, arg.exclude_collection ,arg.user, arg.password, arg.out)

        # List and get the number of files in the bucket
        s3 = boto3.resource('s3')
        if arg.prefix:
            objects=s3.Bucket(name=arg.bucket).objects.filter(Prefix=arg.prefix)
        else:
            objects=s3.Bucket(name=arg.bucket).objects.filter()

        print("Filelist on the S3 bucket:")
        filedict={}
        for object in objects:
            if object.key.startswith(arg.prefix + '/dump-' + arg.database):
              print((object.key))
              filedict.update({object.key: object.last_modified})

        # create new tarball
        print("Creating the tarball:")
        tarball_name="%s-%s.tar.gz" % (arg.out, datetime.strftime(datetime.now(),'%Y-%m-%d-%H%M%S'))
        tarball_cmd="tar -czvf %s %s" % (tarball_name, arg.out)
        tarball_output = subprocess.check_output(tarball_cmd, shell=True)
        print(tarball_output)

        # remove dumped files
        print("Removing temporary dump files...")
        shutil.rmtree(arg.out)

        # upload the new tarball to s3
        remote_file="%s/%s" % (arg.prefix,os.path.basename(tarball_name))
        print("Uploading %s to Amazon S3..." % tarball_name)
        s3_client = boto3.client('s3')
        s3.meta.client.upload_file(tarball_name, arg.bucket, remote_file)

        # remove temporary tarball
        print("Removing temporary local tarball...")
        os.remove(tarball_name)

        # keep de the last N dumps on s3: removes the oldest ones
        # remove the first element of array if prefix (dirname) was used
        prefix= arg.prefix + "/"
        #if arg.prefix:
        #   del filedict[arg.prefix + "/"]
        sorted_filedict=sorted(list(filedict.items()), key=operator.itemgetter(1))
        for item in sorted_filedict[0:len(sorted_filedict)-arg.number]:
            print("Deleting file from S3: %s" % item[0])
            object = s3.Object(arg.bucket, item[0]).delete()

    if arg.method == "snapshot":
       print("Method: EBS snapshot")

       if arg.method == "snapshot" and not arg.volume_id:
          parser.error("The snapshot method requires --volume_id")

       if len(arg.volume_id) == 1:
           # data and journal are in the same volume: no fsyncLock required
           fsyncLock = False
           if not arg.volume_id[0].startswith("vol-"):
               parser.error("Incorrent volume_id")
           volumes_dict = {
                         'data' : arg.volume_id[0],
           }
           # Unless
           if arg.no_journal is not None:
               fsyncLock = arg.no_journal
           if fsyncLock == True:
               print("  fsyncLock: %s" % fsyncLock)
               if arg.user and not arg.password:
                      parser.error("You provided a user but not a password")
               if arg.password and not arg.user:
                      parser.error("You provided a password but not a user")
           else:
               print("  fsyncLock: %s" % fsyncLock)
           print("  Volume: %s" %  arg.volume_id[0])

       if len(arg.volume_id) == 2:
           if arg.user and not arg.password:
              parser.error("You provided a user but not a password")
           if arg.password and not arg.user:
              parser.error("You provided a password but not a user")
           if not arg.volume_id[0].startswith("vol-") or not arg.volume_id[1].startswith("vol-"):
              parser.error("Incorrent volume_id")
           # data and journal resides in a separate volumes: fsyncLock required
           volumes_dict = {
                         'data' : arg.volume_id[0],
                         'journal' : arg.volume_id[1],
                 }
           fsyncLock = True
           print("  fsyncLock: %s" %  fsyncLock)
           print("  Volumes: %s, %s" % (arg.volume_id[0], arg.volume_id[1]))

       if fsyncLock == True:
            try:
                lockres = fsync("lock", arg.host, arg.user, arg.password)
                print ("  Lock result: %s" % lockres)
            except Exception as e:
                print ("  An error ocurred: %s" % e)
       # Para cada volumen llamo a función de creación de snapshot
       snapshots = create_snapshot(arg.region, volumes_dict)
       print ("  waiting for %s to complete" % snapshots)
       try:
           client = boto3.client('ec2', region_name=arg.region)
           waiter = client.get_waiter('snapshot_completed')
           waiter.wait(SnapshotIds=snapshots)
       except botocore.exceptions.WaiterError as e:
           print(e.message)
       # Llamo a funcion fsycLock(stop)
       try:
           lockres = fsync("unlock", arg.host, arg.user, arg.password)
           print ("  Lock result: %s" % lockres)
       except Exception as e:
           print ("  An error ocurred: %s" % e)

if __name__ == '__main__':
    sys.exit(main())
