#!/usr/bin/env python
import boto3
import sys
import argparse
from fabric import Connection
import re
from rich.console import Console
from rich.table import Table

def list_instances(Filter, RegionName, InstanceIds, IgnorePattern):
   ec2 = boto3.resource('ec2', region_name=RegionName)
   instances = ec2.instances.filter(Filters=Filter, InstanceIds=InstanceIds)
   num = 1
   hosts = [] 
   name = {}  
   for i in instances:
       num = num + 1
   if num > 1:
       table = Table()
       table.add_column("num", justify="right", no_wrap=True)
       table.add_column("Name", style="green")
       table.add_column("Public IP", style="red")
       table.add_column("Private IP", style="red")
       table.add_column("ID", justify="right", style="cyan")
       table.add_column("Type", justify="right", style="green")
       table.add_column("Zone", justify="right", style="green")
       table.add_column("VPC", style="cyan")
       table.add_column("Subnet", style="cyan")
       table.add_column("Status")
   num =1
   for i in instances:
      try:
         if i.tags is not None:
           name = next((item for item in i.tags if item["Key"] == "Name"))
         else:
           name['Value'] = ''
      except StopIteration:
         name['Value'] = ''
      
      pattern = re.compile(IgnorePattern)
      if len(IgnorePattern) > 0 and pattern.search(name['Value']):
          #IgnorePattern Found
          num = num + 1
      else:
          if i.state['Name'] == 'stopped':
            table.add_row(
                str(num),
                name['Value'],
                i.public_ip_address,
                i.private_ip_address,
                i.id,
                i.instance_type,
                i.placement['AvailabilityZone'],
                i.vpc_id,
                i.subnet_id,
                i.state['Name'],
                style='italic grey42'
            )
          else:
              table.add_row(
                  str(num),
                  name['Value'],
                  i.public_ip_address,
                  i.private_ip_address,
                  i.id,
                  i.instance_type,
                  i.placement['AvailabilityZone'],
                  i.vpc_id,
                  i.subnet_id,
                  i.state['Name']    
              )
          num = num + 1
          item={'id': i.id, 'public_ip': i.public_ip_address, 'private_ip': i.private_ip_address, 'hostname': name['Value'], 'status': i.state['Name'],}
          hosts.append(item)
   if num > 1:
       console = Console()
       console.print(table)
   return hosts

def execute_cmd(host,user,cmd,connection_method):
    if connection_method == 'bastion-host':
       # The connection user is readed from ./ssh/config file
       result = Connection(host=host, user=user).run(cmd, hide=True, warn=True)
       return result
    if connection_method == 'direct':
        # The connection user is passed as an argument and defaults to ubuntu
       result = Connection(host=host, user=user).run(cmd, hide=True, warn=True)
       return result

def main():
    parser = argparse.ArgumentParser(description='Shows a list with your EC2 instances, then you can execute remote commands on those instances.')
    parser.add_argument('-n', '--name',
                        help="Filter result by name.")
    parser.add_argument('-t', '--type',
                        help="Filer result by type.")
    parser.add_argument('-s', '--status',
                        help="Filter result by status." )
    parser.add_argument('-z', '--zone',
                        help="Filter result by Availability Zone.")
    parser.add_argument('-v', '--vpc',
                        help="Filter result by VPC Id.")
    parser.add_argument('-S', '--subnet',
                        help="Filter result by Subnet Id.")
    parser.add_argument('--public_ip',
                        help="Filter result by public ip address. You can provide the whole IP address string or just a portion of it.")
    parser.add_argument('--private_ip',
                        help="Filter result by private ip adreess. You can provide the whole IP address string or just a portion of it.")
    parser.add_argument('-l', '--id_list',
                        nargs='+', type=str,
                        help="Do not filter the result. Provide a InstanceIds list instead." )
    parser.add_argument('-i', '--ignore', default="",
                        help="Do not show hosts lines containing the \"IGNORE\" pattern in the tag Name" )
    parser.add_argument('-e', '--execute',
                        help="Execute a command on instances")
    parser.add_argument('-r', '--region',
                        help="Specify an alternate region to override \
                              the one defined in the .aws/credentials file")
    parser.add_argument('-u', '--user',
                        help="User to run commands (if -e option is used).\
                              A user is always required, even if you have one defined in .ssh/config file")
    parser.add_argument('-c', '--connection_method',
                        help="The Method to connect to the instance (if -e option is used). \
                              If the instance exposes the SSH port on a public IP, use direct. \
                              Otherwhise choose bastion-host. This method look for the hostname and username \
                              inside the .ssh/config file to reach the target instance.",
                        choices=['direct', 'bastion-host'],
                        default="direct")

    arg = parser.parse_args()

    # Default filter if no options are specified
    filter=[]
    InstanceIds=[]
    IgnorePattern=""
    
    if arg.execute and (arg.user is None):
       parser.error("--execute requires --user.")
    
    if arg.name:
        filter.append({'Name': 'tag-value', 'Values': ["*" + arg.name + "*"]})

    if arg.type:
        filter.append({'Name': 'instance-type', 'Values': ["*" + arg.type + "*"]})

    if arg.status:
        filter.append({'Name': 'instance-state-name', 'Values': ["*" + arg.status + "*"]})

    if arg.vpc:
        filter.append({'Name': 'vpc-id', 'Values': ["*" + arg.vpc + "*"]})

    if arg.zone:
        filter.append({'Name': 'availability-zone', 'Values': ["*" + arg.zone + "*"]})
    
    if arg.subnet:
        filter.append({'Name': 'subnet-id', 'Values': ["*" + arg.subnet + "*"]})

    if arg.public_ip:
        filter.append({'Name': 'ip-address', 'Values': ["*" + arg.public_ip + "*"]})

    if arg.private_ip:
        filter.append({'Name': 'private-ip-address', 'Values': ["*" + arg.private_ip + "*"]})

    if arg.id_list:
        InstanceIds=arg.id_list
    
    if arg.ignore:
        IgnorePattern=arg.ignore
    
    if arg.region: 
       client = boto3.client('ec2')
       regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
       if arg.region not in regions:
          sys.exit("ERROR: Please, choose a valid region.")

    hosts=list_instances(filter,arg.region,InstanceIds,IgnorePattern)
    names = ""

    if arg.execute:
       if arg.connection_method == 'direct':
          target='public_ip'
       if arg.connection_method == 'bastion-host':
          target='hostname'

       for item in hosts:
          names = names + " " + "[green]" + item["hostname"] + "[/green]:[cyan]" + item["id"] + "[/cyan] " 

       console = Console() 
       console.print("Command to execute: %s" % arg.execute)
       console.print("Executed by: %s" % arg.user)
       console.print("Hosts list: %s" % names)
       with console.status("[bold green]Working on remote execution...[/bold green]") as status:
           for item in hosts:
              if item["status"] == 'running':
                 if item["public_ip"] is None and arg.connection_method == 'direct':
                    console.rule("[green]%s[/green][cyan] : %s[/cyan] is not reachable using direct method. Use the bastion-host instead  (command execution skiped)" % (item["hostname"], item["id"]))
                    continue
                 console.rule("[green]%s[/green][cyan] : %s[/cyan]" % (item["hostname"], item["id"]), align='center')
                 print(execute_cmd(item[target], arg.user, arg.execute, arg.connection_method))
              else:
                 console.rule("[green]%s[/green][cyan] : %s[/cyan] is not running (command execution skiped)" % (item["hostname"], item["id"]))

if __name__ == '__main__':
    sys.exit(main())
