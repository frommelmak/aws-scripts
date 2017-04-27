aws-scripts
===========

Here you will find some useful AWS scripts I use from time to time.

All the scripts relies on [Boto](http://aws.amazon.com/sdkforpython/), a Python package that provides interfaces to Amazon Web Services.

So, to use these scripts, you need to install Boto and provide your AWS credentinals:

To install Boto and all the required Python packages just clone this repository and type:

```
pip install -r requirements.txt
```

If dependencies are already satisfied, nothing will be installed.

To provide your AWS credentials use the boto/boto3 config file `~/.aws/config`:

``` ini
[default]
aws_access_key_id = <XXXXXXXXXXXXXXXXXXX>
aws_secret_access_key = <xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx>
region=xx-xxxx-x
```

ec2-instances.py
----------------

List the EC2 instances including the Name Tag, the public IP, the type, the vpc ID and the status.

You can filter the result by name, type and/or status.

Finally you can execute remote commands on all the instances returned by the filter.

The '-h' option shows you how to use the available options.

``` bash
usage: ec2-instances.py [-h] [-n NAME] [-t TYPE] [-s STATUS] [-e EXECUTE]
                        [-u USER]

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Filter result by name.
  -t TYPE, --type TYPE  Filer result by type.
  -s STATUS, --status STATUS
                        Filter result by status.
  -e EXECUTE, --execute EXECUTE
                        Execute a command on instances
  -u USER, --user USER  User to run commands if -e option is used. Ubuntu user
                        is used by default
```

ec2-elb.py
----------

Lists all your Elastic Load Balancers and his related instances.

``` bash
usage: ec2-elb.py [-h]

For every Elastic Load Balancer list the attached instances

optional arguments:
  -h, --help  show this help message and exit
```

ec2-snap-mgmt.py
----------------

With this script you can see the relationships between your snapshots and your EBS volumes and AMIs. This allows you to choose the snapshots you don't need to keep in the AWS S3 service.

By default the script shows all the volumes and AMIs related to each snapshost.

You you can also show all the snapshots related with each volume. This option is specially usefull when you only want to keep a certain number of snapshots per volume.

Finally, you can show all the snapshots related with each AMI.

The '-h' option shows you how to use the available options.

``` bash
usage: ec2-snap-mgmt.py [-h] [-v {orphan,volumes}] owner_id

positional arguments:
  owner_id              12-digit AWS Account Number

optional arguments:
  -h, --help            show this help message and exit
  -v {orphan,volumes,images}, --view {orphan,volumes,images}
                        Available views: orphan and volumes. Orphan is the
                        default one.
```

The script doesn't delete anything actually, just shows you the relationship in a tree view.

s3-mongodump.py
---------------

This is a tool to make mongodb backups on Amazon s3.

It uses mongodump to perform a binary backup of your local or remote mongodb instance. The dumped files are compressed in a tarball file and uploaded to a Amazon S3 bucket.
You can specify the number of copies to retain in the bucket. The oldest ones will be automatically removed.

``` bash
usage: s3-mongodump.py [-h] [-u USER] [-p PASSWORD] [-H HOST] [-d DATABASE]
                       [-o OUT] [-n NUMBER] -b BUCKET [-P PREFIX]

A tool to make mongodb backups on Amazon s3

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  Mongodb user (optional)
  -p PASSWORD, --password PASSWORD
                        Mongodb password (optional)
  -H HOST, --host HOST  Mongodb host: <hostname>:<port>.
  -d DATABASE, --database DATABASE
                        The database to backup (all if not provided)
  -o OUT, --out OUT     The output directory for dumped files
  -n NUMBER, --number NUMBER
                        Number of copies to retain in the S3 bucket
  -b BUCKET, --bucket BUCKET
                        Amazon s3 bucket.
  -P PREFIX, --prefix PREFIX
                        For grouped objects aka s3 folders, provide the prefix
                        key
```

route53-set-hostname.py
-----------------------

This script allows you to automatically set predictable DNS records for instances launched using AWS Auto Scaling. 

It is intended to be executed from the ec2 instance at launch time.
The script looks for an available name matching the provided pattern in the DNS zone. Then, it adds this name as a CNAME record in the DNS zone pointing to the EC2 instance public name.

``` bash
usage: route53-set-hostname.py [-h] --HostedZoneId HOSTEDZONEID --HostStr
                               HOSTSTR [--rangeSize RANGESIZE] [--dryrun]

AWS Route53 hostname managment for Autoscaled EC2 Instances

optional arguments:
  -h, --help            show this help message and exit
  --HostedZoneId HOSTEDZONEID
                        The ID of the hosted zone where the new resource
                        record will be added.
  --HostStr HOSTSTR     The host string used to build the new name
  --rangeSize RANGESIZE
                        The maximun number to be assigned. The first available
                        will be used
  --dryrun              Shows what is going to be done but doesn't change
                        anything actually
```

Example:

``` bash
user@host:~$ ./route53-set-hostname.py --HostedZoneId XXXXXXXXXXXXXX --HostStr websrv --rangeSize 10
15:41:58 06/09/16: creating CNAME websrv03.example.com. -> ec2-XX-XX-XXX-XX.compute-1.amazonaws.com......INSYNC
```

route53-del-hostname.py
-----------------------

This script is executed from the ec2 instance at shutdown.
The script delete his host record zone from the passed DNS zone identifier.

``` bash
usage: route53-del-hostname.py [-h] --HostedZoneId HOSTEDZONEID [--dryrun]

AWS Route53 hostname managment for Autoscaled EC2 Instances

optional arguments:
  -h, --help            show this help message and exit
  --HostedZoneId HOSTEDZONEID
                        The ID of the hosted zone where the new resource
                        record will be added.
  --dryrun              Shows what is going to be done but doesn't change
                        anything actually
```

s3-download-file.py
-------------------

This script just download the requested S3 object.

``` bash
usage: s3-download-file.py [-h] -b BUCKET -o OBJECTKEY -f FILEPATH

Donwload file from AWS S3

optional arguments:
  -h, --help            show this help message and exit
  -b BUCKET, --bucket BUCKET
                        The bucket name.
  -o OBJECTKEY, --objectkey OBJECTKEY
                        The host string used to build the new name
  -f FILEPATH, --filepath FILEPATH
                        The filepath of the file to be saved
```

lifecycle-hook-worker.py
------------------------

As its own name says, this worker is designed to use auto scaling [lifecycle hooks](http://docs.aws.amazon.com/autoscaling/latest/userguide/lifecycle-hooks.html).

The process looks for incoming messages into the SQS queue asociated with the autoscaling group. Then, when a message comes for the instance, it is consumed and the associated custom action is triggered. Finally, using the lifecyle action token, the worker completes the autoscaling action going on with the launch or ending the instance action.

``` bash
usage: lifecycle-hook-worker.py [-h] -q QUEUE -s {LAUNCHING,TERMINATING} -g
                                GROUP -H HOOKNAME -e EXECUTE [-w WAIT]

SQS Lifecycle hook consumer and trigger

optional arguments:
  -h, --help            show this help message and exit
  -q QUEUE, --queue QUEUE
                        Queue resource.
  -s {LAUNCHING,TERMINATING}, --state {LAUNCHING,TERMINATING}
                        Indicates if the consumer is waiting for LAUNCHING or
                        TERMINATING state
  -g GROUP, --group GROUP
                        Auto Scaling Group Name
  -H HOOKNAME, --hookName HOOKNAME
                        Life Cycle Hook Name
  -e EXECUTE, --execute EXECUTE
                        The filepath of the triggered script
  -w WAIT, --wait WAIT  Time between query loops in seconds (default: 60)
```

rds-instances.py
----------------

Shows the main info regarding all the RDS instances such as: endpoint, engine, version, status etc.

``` bash
usage: rds-instances.py [-h]

List all the RDS instances

optional arguments:
  -h, --help  show this help message and exit
```
