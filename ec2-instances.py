#!/usr/bin/env python
import boto3
import sys
import argparse
import paramiko


def list_instances(Filter):
   ec2 = boto3.resource('ec2')
   instances = ec2.instances.filter(Filters=Filter)
   columns_format="%-3s %-26s %-16s %-16s %-16s"
   print columns_format % ("num", "Name", "Public IP", "Type", "Status")
   num = 1
   hosts = {}
   for i in instances:
      print columns_format % (num, i.tags[0]['Value'], i.public_ip_address, i.instance_type, i.state['Name'])
      num = num + 1
      hosts[i.tags[0]['Value']]=i.public_ip_address
   return hosts

def execute_cmd(host,user,cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout=stdout.read()
    ssh.close()
    return stdout

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name',
                        help="Filter result by name.")
    parser.add_argument('-t', '--type',
                        help="Filer result by type.")
    parser.add_argument('-s', '--status',
                        help="Filter result by status." )
    parser.add_argument('-e', '--execute',
                        help="Execute a command on instances")
    parser.add_argument('-u', '--user', default="ubuntu",
                        help="User to run commands if -e option is used.")

    arg = parser.parse_args()

    # Default filter if no options are specified
    filter=[{
             'Name': 'tag-key',
             'Values': ['Name'],
           }]

    if arg.name:
        filter.append({'Name': 'tag-value', 'Values': ["*" + arg.name + "*"]})

    if arg.type:
        filter.append({'Name': 'instance-type', 'Values': ["*" + arg.type + "*"]})

    if arg.status:
        filter.append({'Name': 'instance-state-name', 'Values': ["*" + arg.status + "*"]})

    hosts=list_instances(filter)

    if arg.execute:
       print "Command to execute: %s" % arg.execute
       print "Command executed by the user: %s" % arg.user
       print "Host list: %s" % hosts
       for name in hosts:
          print "::: %s" % name
          print execute_cmd(hosts[name], arg.user, arg.execute)


if __name__ == '__main__':
    sys.exit(main())
