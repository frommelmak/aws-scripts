aws-scripts
===========

Here you will find some useful AWS scripts I use from time to time.

All the scripts relies on [Boto](http://aws.amazon.com/sdkforpython/), a Python package that provides interfaces to Amazon Web Services.

So, to use these scripts, you need to install Boto and provide your AWS credentinals:

To install Boto just type:

```
pip install boto
```

To provide your AWS credentials export the following environment variables: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. Alternatively, use the boto config file `~/.boto`:

```
[Credentials]
aws_access_key_id = <XXXXXXXXXXXXXXXXXXX>
aws_secret_access_key = <xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx>
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

ec2-instances.py
----------------

List the EC2 instances including the Name Tag, the public IP, the type and the status.

You can filter the result by name, type and/or status.

The '-h' option shows you how to use the available options.

```
usage: ec2-instances.py [-h] [-n NAME] [-t TYPE] [-s STATUS]

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Filter result by name.
  -t TYPE, --type TYPE  Filer result by type.
  -s STATUS, --status STATUS
                        Filter result by status.
```
