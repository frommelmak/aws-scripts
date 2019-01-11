#!/usr/bin/env python
import boto3
import sys
import argparse
import paramiko


def list_instances(Filter, RegionName, InstanceIds):
   ec2 = boto3.resource('ec2', region_name=RegionName)
   instances = ec2.instances.filter(Filters=Filter, InstanceIds=InstanceIds)
   columns_format="%-3s %-26s %-15s %-15s %-20s %-10s %-11s %-12s %-16s"
   print columns_format % ("num", "Name", "Public IP", "Private IP", "ID", "Type", "Zone","VPC", "Status")
   num = 1
   hosts = [] 
   name = {}  
   for i in instances:
      try:
         if i.tags is not None:
           name = (item for item in i.tags if item["Key"] == "Name").next()
         else:
           name['Value'] = ''
      except StopIteration:
         name['Value'] = ''
      
      print columns_format % (
                               num,
                               name['Value'], 
                               i.public_ip_address,
                               i.private_ip_address,
                               i.id,
                               i.instance_type,
                               i.placement['AvailabilityZone'],
                               i.vpc_id,
                               i.state['Name']
                             )
      num = num + 1
      item={'id': i.id, 'ip': i.public_ip_address, 'hostname': name['Value'], 'status': i.state['Name'],}
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
    parser.add_argument('-l', '--id_list',
                        nargs='+', type=str,
                        help="Provide a list of InstanceIds." )
    parser.add_argument('-e', '--execute',
                        help="Execute a command on instances")
    parser.add_argument('-r', '--region',
                        help="Specify an alternate region to override \
                              the one defined in the .aws/credentials file")
    parser.add_argument('-u', '--user', default="ubuntu",
                        help="User to run commands if -e option is used.\
                              Ubuntu user is used by default")

    arg = parser.parse_args()

    # Default filter if no options are specified
    filter=[]
    InstanceIds=[]

    if arg.name:
        filter.append({'Name': 'tag-value', 'Values': ["*" + arg.name + "*"]})

    if arg.type:
        filter.append({'Name': 'instance-type', 'Values': ["*" + arg.type + "*"]})

    if arg.status:
        filter.append({'Name': 'instance-state-name', 'Values': ["*" + arg.status + "*"]})

    if arg.id_list:
        InstanceIds=arg.id_list
    
    if arg.region: 
       client = boto3.client('ec2')
       regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
       if arg.region not in regions:
          sys.exit("ERROR: Please, choose a valid region.")

    hosts=list_instances(filter,arg.region,InstanceIds)
    names = ""

    if arg.execute:
       for item in hosts:
          names = names + " " + item["hostname"] + "(" + item["id"] + ")"
       print "\nCommand to execute: %s" % arg.execute
       print "Executed by: %s" % arg.user
       print "Hosts list: %s\n" % names 
       for item in hosts:
          if item["status"] == 'running':
             print "::: %s (%s)" % (item["hostname"], item["id"])
             stdout,stderr = execute_cmd(item["ip"], arg.user, arg.execute)
             print stdout 
             print stderr
          else:
             print "::: %s (%s) is not running (command execution skiped)" % (item["hostname"], item["id"])

if __name__ == '__main__':
    sys.exit(main())
