[![PyPI](https://img.shields.io/pypi/v/aws-scripts.svg)](https://pypi.org/project/aws-scripts/)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://opensource.org/licenses/MIT)

aws-scripts
===========

Here you will find some useful AWS scripts I use from time to time.

All the scripts relies on [Boto](http://aws.amazon.com/sdkforpython/), a Python package that provides interfaces to Amazon Web Services.

So, to use these scripts, you need to install Boto and provide your AWS credentinals:

To install aws-scripts and all the required Python packages just type:

```
pip install aws-scripts 
```

If dependencies are already satisfied, nothing will be installed.

To provide your AWS credentials use the boto/boto3 config file `~/.aws/credentials`:

``` ini
[default]
aws_access_key_id = <XXXXXXXXXXXXXXXXXXX>
aws_secret_access_key = <xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx>
region=xx-xxxx-x
```

> Note that you can use the environment variable: ```AWS_DEFAULT_REGION=xx-xxxx-x``` to override the default region on the config file.
> In the ec2-instances.py script you can also use the ```--region``` option for the same purpose 

ec2-instances.py
----------------

List the EC2 instances including the Name Tag, IP, type, zone, vpc, ID and the status.

You can filter the result by name, type and/or status. Or you can provide a list of instance IDs instead.

Finally you can execute remote commands on all the instances returned by the filter or the list.

The '-h' option shows you how to use the available options.

```
usage: ec2-instances.py [-h] [-n NAME] [-t TYPE] [-s STATUS]
                        [-l ID_LIST [ID_LIST ...]] [-e EXECUTE] [-r REGION]
                        [-u USER]

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Filter result by name.
  -t TYPE, --type TYPE  Filer result by type.
  -s STATUS, --status STATUS
                        Filter result by status.
  -l ID_LIST [ID_LIST ...], --id_list ID_LIST [ID_LIST ...]
                        Provide a list of InstanceIds.
  -e EXECUTE, --execute EXECUTE
                        Execute a command on instances
  -r REGION, --region REGION
                        Specify an alternate region to override the one
                        defined in the .aws/credentials file
  -u USER, --user USER  User to run commands if -e option is used. Ubuntu user
                        is used by default
```

ec2-reserved.py
----------------

Lists details of all your Instance Reservations, including a summary of the active reservations by type and size.

The summary also shows your reserved active capacity after apply the normalization factor. This is useful to compare the reserved capacity with the deployed in production.

You can also use the option `--create-google-calendar-events` to add the expiration date of the active reservations in your Google Calendar Account.

```
usage: ec2-reserved.py [-h]
                        [-s {payment-pending,active,payment-failed,retired}]
                        [--create-google-calendar-events] [-t TYPE]

Show reserved EC2 instances

optional arguments:
  -h, --help            show this help message and exit
  -s {payment-pending,active,payment-failed,retired}, --state {payment-pending,active,payment-failed,retired}
                        Filer result by reservation state.
  --create-google-calendar-events
                        Create events in your Google Calendar, using the
                        expiration dates of your active reservations
  -t TYPE, --type TYPE  Filer result by instance type.
```

To use the Google calendar feature you just have to [enable the calendar API in your Google Account](https://console.developers.google.com) and create a calendar called aws in the [Google Calendar](http://calendar.google.com/). Then create the *OAuth client ID* credentials. Download the credentials file and save it as `client_secret.json` in the aws-scripts folder repo. When you run the script using the `--create-google-calendar-events` option for the first time, a web browser will be opened asking your to login with the Google account you want to use.

Then, whenever you buy new reservations on Amazon Web Services, you can add the new reservations in your calendar by just running the script.

ec2-elb.py
----------

Lists all your Elastic Load Balancers and his related instances.

```
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

```
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

```
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

```
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

```
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

```
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

```
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

```
usage: rds-instances.py [-h]

List all the RDS instances

optional arguments:
  -h, --help  show this help message and exit
```
