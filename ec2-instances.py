#!/usr/bin/env python
import boto3
import sys
import argparse
import paramiko


def list_instances(Filter):
   ec2 = boto3.resource('ec2')
   instances = ec2.instances.filter(Filters=Filter)
   columns_format="%-3s %-26s %-16s %-16s %-20s %-12s %-12s %-16s"
   print columns_format % ("num", "Name", "Public IP", "Private IP", "ID", "Type", "VPC", "Status")
   num = 1
   hosts = [] 
   name = {}  
   for i in instances:
      try:
         name = (item for item in i.tags if item["Key"] == "Name" ).next()
      except StopIteration:
         name['Value'] = ''
      
      print columns_format % (
                               num,
                               name['Value'], 
                               i.public_ip_address,
                               i.private_ip_address,
                               i.id,
                               i.instance_type,
                               i.vpc_id,
                               i.state['Name']
                             )
      num = num + 1
      item={'id': i.id, 'ip': i.public_ip_address, 'hostname': name['Value'],}
      hosts.append(item)
   return hosts

def execute_cmd(host,user,cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
       ssh.connect(host, username=user)
       stdin, stdout, stderr = ssh.exec_command(cmd)
       stdout=stdout.read()
       stderr=stderr.read()
       ssh.close()
       return stdout,stderr
    except paramiko.AuthenticationException, e:
       return "Authentication Error trying to connect into the host %s with the user %s. Plese review your keys" % (host, user), e 

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
                        help="User to run commands if -e option is used.\
                              Ubuntu user is used by default")

    arg = parser.parse_args()

    # Default filter if no options are specified
    filter=[]

    if arg.name:
        filter.append({'Name': 'tag-value', 'Values': ["*" + arg.name + "*"]})

    if arg.type:
        filter.append({'Name': 'instance-type', 'Values': ["*" + arg.type + "*"]})

    if arg.status:
        filter.append({'Name': 'instance-state-name', 'Values': ["*" + arg.status + "*"]})

    hosts=list_instances(filter)
    names = ""
    for item in hosts:
       names = names + " " + item["hostname"] + "(" + item["id"] + ")"

    if arg.execute:
       print "\nCommand to execute: %s" % arg.execute
       print "Executed by: %s" % arg.user
       print "Hosts list: %s\n" % names 
       for item in hosts:
          print "::: %s (%s)" % (item["hostname"], item["id"])
          stdout,stderr = execute_cmd(item["ip"], arg.user, arg.execute)
          print stdout 
          print stderr

if __name__ == '__main__':
    sys.exit(main())
