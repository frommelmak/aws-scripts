[![PyPI](https://img.shields.io/pypi/v/aws-scripts.svg)](https://pypi.org/project/aws-scripts/)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://opensource.org/licenses/MIT)

aws-scripts
===========

Here you will find some useful AWS scripts I use often.


All the scripts relies on [Boto](http://aws.amazon.com/sdkforpython/), a Python package that provides interfaces to Amazon Web Services.

So, to use these scripts, you need to install Boto and provide your AWS credentinals:

To install aws-scripts and all the required Python packages just type:

```
pip install aws-scripts 
```

If dependencies are already satisfied, nothing will be installed.

If you already have aws-scripts installed in your computer you can update to the latest version as follows:

```
pip install --upgrade aws-scripts
```

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

Lists the EC2 instances including the Name Tag, IP, type, zone, vpc, subnet and the status.

You can filter the result by name, type, status and/or public or private IP address. Or you can provide a list of instance IDs instead.

Finally you can execute remote commands on all the instances returned by the filter or the list.

The execution method support both: direct connections against the public instance IP or using a bastion host.

When this method is used, the .ssh/config file is used to establish the connection.

![Demo](https://github.com/frommelmak/aws-scripts/raw/master/img/demo.png)

The '-h' option shows you how to use the available options.

```
usage: ec2-instances.py [-h] [-n NAME] [-t TYPE] [-s STATUS] [-z ZONE] [-v VPC] [-S SUBNET] [--public_ip PUBLIC_IP] [--private_ip PRIVATE_IP] [-l ID_LIST [ID_LIST ...]] [-i IGNORE] [-e EXECUTE] [-r REGION]
                        [-u USER] [-c {direct,bastion-host}]

Shows a list with your EC2 instances, then you can execute remote commands on those instances.

options:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Filter result by name.
  -t TYPE, --type TYPE  Filer result by type.
  -s STATUS, --status STATUS
                        Filter result by status.
  -z ZONE, --zone ZONE  Filter result by Availability Zone.
  -v VPC, --vpc VPC     Filter result by VPC Id.
  -S SUBNET, --subnet SUBNET
                        Filter result by Subnet Id.
  --public_ip PUBLIC_IP
                        Filter result by public ip address. You can provide the whole IP address string or just a portion of it.
  --private_ip PRIVATE_IP
                        Filter result by private ip adreess. You can provide the whole IP address string or just a portion of it.
  -l ID_LIST [ID_LIST ...], --id_list ID_LIST [ID_LIST ...]
                        Do not filter the result. Provide a InstanceIds list instead.
  -i IGNORE, --ignore IGNORE
                        Do not show hosts lines containing the "IGNORE" pattern in the tag Name
  -e EXECUTE, --execute EXECUTE
                        Execute a command on instances
  -r REGION, --region REGION
                        Specify an alternate region to override the one defined in the .aws/credentials file
  -u USER, --user USER  User to run commands (if -e option is used). A user is always required, even if you have one defined in .ssh/config file
  -c {direct,bastion-host}, --connection_method {direct,bastion-host}
                        The Method to connect to the instance (if -e option is used). If the instance exposes the SSH port on a public IP, use direct. Otherwhise choose bastion-host. This method look for
                        the hostname and username inside the .ssh/config file to reach the target instance.
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


ec2-instance-state.py
---------------------
Set the desired state for an EC2 instance or a list of instances.

You can use it form a cron task in order to manage the instance state of one or several instances.
You can even use it without providing the IAM user credentials, thanks to the assume role support.

The '-h' optipn shows you how to use the available options.

```
usage: ec2-instance-state.py [-h] [-s {stop,start,reboot,terminate}] -l ID_LIST [ID_LIST ...] [--role_arn ROLE_ARN] [-r REGION]

Set desired EC2 instance state

optional arguments:
  -h, --help            show this help message and exit
  -s {stop,start,reboot,terminate}, --state {stop,start,reboot,terminate}
                        Set the desired state for the instances provided
  -l ID_LIST [ID_LIST ...], --id_list ID_LIST [ID_LIST ...]
                        InstanceIds list
  --role_arn ROLE_ARN   If the script run on an EC2 instance with an IAM role attached, then the Security Token Service will provide a set of temporary credentials allowing the actions of the assumed role.
                        With this method, no user credentials are required, just the Role ARN to be assumed.
  -r REGION, --region REGION
                        Specify an alternate region to override the one defined in the .aws/credentials file
```

This is an example of the minimun permissions required in the Role Policy in order to auto-stop an instance from a cron job.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "ec2:StopInstances",
            "Resource": "arn:aws:ec2:eu-west-1:<ACCOUNT_ID>:instance/<INSTANCE_ID>"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::<ACCOUNT_ID>:role/<AUTOSTOP_ROLE_NAME>"
        }
    ]
}
```

ec2-sg.py
---------

Lists the EC2 Security Groups within an AWS region. The result can be filtered by name.
You can also show the Inbound and Outbound rules of the chosen security group.

As a sysadmin and/or developer, you or your team mates, will probably find yourself updating your public IP address frequently in order to gain SSH access to your EC2 instances.

This command help you to do so. Just use the argument `--allow_my_public_ip` providing the Security Group ID and the Security Group Rule ID you want to update. The command will find out your public IP and will update the rule allowing you the SSH access.

```
usage: ec2-sg.py [-h] [-n NAME] [-l GID_LIST [GID_LIST ...]] [-r REGION] [-s SHOW] [--allow_my_public_ip ALLOW_MY_PUBLIC_IP] [--security_group_rule_id SECURITY_GROUP_RULE_ID] [--description DESCRIPTION]

Security Groups Management

options:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Filter result by group name.
  -l GID_LIST [GID_LIST ...], --gid_list GID_LIST [GID_LIST ...]
                        Do not filter the result. Provide a GroupIds list instead.
  -r REGION, --region REGION
                        Specify an alternate region to override the one defined in the .aws/credentials file
  -s SHOW, --show SHOW  Show inbound and outbound rules for the provided SG ID
  --allow_my_public_ip ALLOW_MY_PUBLIC_IP
                        Modify the SSH inbound rule with your current public IP address inside the provided Security Group ID.
  --security_group_rule_id SECURITY_GROUP_RULE_ID
                        Modify the SSH inbound rule with your current public IP address inside the provided Security Group Rule ID
  --description DESCRIPTION
                        Allows you to append a string to the rule description field
```

ec2-ebs.py
----------
Lists the EC2 EBS volumes including the Name Tag, size, device, ID, attached instance ID, Attached instance Tag Name, type, IOPS, zone and status.

You can filter the result by type, status and Tag name.

The '-h' option shows you how to use the available options.

```
usage: ec2-ebs.py [-h] [-n NAME] [-t {gp2,io1,st1,sc1,standard}] [-s {creating,available,in-use,deleting,deleted,error}]

List all the Elastic Block Storage volumes

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Filter result by name.
  -t {gp2,io1,st1,sc1,standard}, --type {gp2,io1,st1,sc1,standard}
                        Filer result by type.
  -s {creating,available,in-use,deleting,deleted,error}, --status {creating,available,in-use,deleting,deleted,error}
                        Filter result by status.
```

ec2-elb.py
----------

Lists all your Elastic Load Balancers and his related instances.

```
usage: ec2-elb.py [-h] [-t {classic,current,all}]

For every Elastic Load Balancer list the attached instances

options:
  -h, --help            show this help message and exit
  -t {classic,current,all}, --type {classic,current,all}
                        It shows the current generation of ELBs (Application, Network and/or Gateway) and/or the previous one (Classic).
```

ec2-tg.py
---------

Without parameters just lists the target groups within a region. You can also list the targets in a given target group. Finally, you can also register or deregister targets to/from a group.

```
usage: ec2-tg.py [-h] [-s SHOW] [-a {register,deregister,details}] [--target_type {instances,ip_address,lambda_function,alb}] [--targets_id_list TARGETS_ID_LIST [TARGETS_ID_LIST ...]]
                 [--target_group_arn TARGET_GROUP_ARN] [--role_arn ROLE_ARN] [-r REGION]

Shows a list of Target Grops. Also allows you to register/unregister targets in/from a provided Targer Group

options:
  -h, --help            show this help message and exit
  -s SHOW, --show SHOW  Shows the target for the provided Target Group ARN
  -a {register,deregister,details}, --action {register,deregister,details}
                        Set the desired action.
  --target_type {instances,ip_address,lambda_function,alb}
                        Set the desired state for the instances provided
  --targets_id_list TARGETS_ID_LIST [TARGETS_ID_LIST ...]
                        Targets Id list
  --target_group_arn TARGET_GROUP_ARN
                        Target Group ARN
  --role_arn ROLE_ARN   If the script run on an EC2 instance with an IAM role attached, then the Security Token Service will provide a set of temporary credentials allowing the actions of the assumed role.
                        With this method, no user credentials are required, just the Role ARN to be assumed.
  -r REGION, --region REGION
                        Specify the region to override the one setted in the credentials file or if you are using --role_arn.
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

mongodb-backup.py
-----------------

This is a tool to make MongoDB backups on Amazon.

Two methods are supported: dump and snapshot.

- For the first one It uses `mongodump` to perform a binary backup of your local or remote MongoDB instance. The dumped files are compressed in a tarball file and uploaded to a Amazon S3 bucket.
- For the snapshot method, you can provide the data and / or the journal volumes and the script automatically will lock the database and will suspend all the writes during the backup process to ensure the consistency of the backup if required.

For the dump method, you can specify the number of copies to retain in the bucket or in the EC2 snapshot area. The oldest ones will be automatically removed.

```
usage: mongodb-backup.py [-h] [-m {dump,snapshot}] [-u USER] [-p PASSWORD] [-H HOST] [-d DATABASE] [-c COLLECTION] [-e EXCLUDE_COLLECTION] [-o OUT] [-n NUMBER] [-b BUCKET] [-P PREFIX]
                         [-v VOLUME_ID [VOLUME_ID ...]] [--no_journal] [-r REGION]

A tool to make mongodb backups on Amazon

optional arguments:
  -h, --help            show this help message and exit
  -m {dump,snapshot}, --method {dump,snapshot}
                        Backup method. Dump if none is provided
  -u USER, --user USER  Mongodb user (optional)
  -p PASSWORD, --password PASSWORD
                        Mongodb password (optional)
  -H HOST, --host HOST  Mongodb host: <hostname>:<port>. By default: localhost:27017
  -d DATABASE, --database DATABASE
                        For the dump method: The database to backup (all if not provided)
  -c COLLECTION, --collection COLLECTION
                        For the dump method: The collection to backup. Requires '-d' option
  -e EXCLUDE_COLLECTION, --exclude_collection EXCLUDE_COLLECTION
                        For the dump method: The collection to exclude from backup. Requires '-d' option
  -o OUT, --out OUT     For the dump method: The output directory for dumped files
  -n NUMBER, --number NUMBER
                        Number of copies to retain
  -b BUCKET, --bucket BUCKET
                        For the dump method: Amazon s3 bucket.
  -P PREFIX, --prefix PREFIX
                        For the dump method: For grouped objects aka s3 folders, provide the prefix key
  -v VOLUME_ID [VOLUME_ID ...], --volume_id VOLUME_ID [VOLUME_ID ...]
                        For the snapshot method: Provide the data and journal volume_id list to snapshot: If data and journal resides in a separate volumes, both volumes are required.
  --no_journal          For the snapshot method: If pressent, the instance is either running without journaling or has the journal files on a separate volume, you must flush all writes to disk and lock the
                        database to prevent writes during the backup process.
  -r REGION, --region REGION
                        Specify an alternate region to override the one defined in the .aws/credentials file

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

The process looks for incoming messages into the SQS queue associated with the autoscaling group. Then, when a message comes for the instance, it is consumed and the associated custom action is triggered. Finally, using the lifecycle action token, the worker completes the autoscaling action going on with the launch or ending the instance action.

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
