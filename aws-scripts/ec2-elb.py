#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
import argparse
from rich.tree import Tree
from rich import print
from rich.progress import track

def get_name_tag(ec2, id):
   instance = ec2.Instance(id)
   name=""
   for i in range(len(instance.tags)):
       if instance.tags[i]['Key'] == 'Name':
           name = instance.tags[i]['Value']
   return name

def list_elb(ec2, region):
    client = boto3.client('elb')
    response = client.describe_load_balancers()
    tree = Tree("[bold white]Classic Elastic Load Balancers in the "+region+" AWS region")
    for elb in track(range(len(response.get('LoadBalancerDescriptions'))), description="Procesing..."):
      load_balancer_name = response.get('LoadBalancerDescriptions')[elb].get('LoadBalancerName')
      instance_state = client.describe_instance_health(LoadBalancerName=load_balancer_name)
      elb_tree = tree.add(":file_folder: [bold white]"+load_balancer_name)
      for instance in range(len(response.get('LoadBalancerDescriptions')[elb].get('Instances'))):
         track(range(20), description="Processing...")
         instance_id = instance_state.get('InstanceStates')[instance].get('InstanceId')
         if instance_state.get('InstanceStates')[instance].get('State') == 'OutOfService':
             branch = elb_tree.add("[cyan]"+instance_id+" [white]("+get_name_tag(ec2, instance_id)+")"+" Status: [red]"+instance_state.get('InstanceStates')[instance].get('State'))
         else:
             branch = elb_tree.add("[cyan]"+instance_id+" [white]("+get_name_tag(ec2, instance_id)+")"+" Status: [green]"+instance_state.get('InstanceStates')[instance].get('State'))
    print(tree)

def list_elbv2(ec2, region):
    client = boto3.client('elbv2')
    response = client.describe_load_balancers()
    tree = Tree("[bold white]Current Generation of Elastic Load Balancers in %s AWS region" % region)
    for elb in track(range(len(response.get('LoadBalancers'))), description="Procesing..."):
      load_balancer_name = response.get('LoadBalancers')[elb].get('LoadBalancerName')
      load_balancer_arn = response.get('LoadBalancers')[elb].get('LoadBalancerArn')
      load_balancer_type = response.get('LoadBalancers')[elb].get('Type')
      load_balancer_tg = client.describe_target_groups(LoadBalancerArn=load_balancer_arn)
      elb_branch = tree.add(":file_folder:[bold white] "+load_balancer_name+" Type: "+load_balancer_type)
      tg_folder = elb_branch.add(":file_folder: Target Groups")
      for tg in range(len(load_balancer_tg.get('TargetGroups'))):
          tg_dict = load_balancer_tg.get('TargetGroups')[tg]
          tg_branch = tg_folder.add(":file_folder:[bold white] "+tg_dict.get('TargetGroupName')+" [not bold]Type: "+tg_dict.get('TargetType'))
          target_health = client.describe_target_health(TargetGroupArn=tg_dict.get('TargetGroupArn'))
          for t in range(len(target_health.get('TargetHealthDescriptions'))):
              target_id=target_health.get('TargetHealthDescriptions')[t].get('Target').get('Id')
              target_state=target_health.get('TargetHealthDescriptions')[t].get('TargetHealth').get('State')
              target_state_desc=target_health.get('TargetHealthDescriptions')[t].get('TargetHealth').get('Description')
              # Target Type: instance'|'ip'|'lambda'|'alb'
              if tg_dict.get('TargetType') == 'instance':
                  target_name=get_name_tag(ec2, target_id)
              elif tg_dict.get('TargetType') == 'ip':
                  target_name="ip"
              elif tg_dict.get('TargetType') == 'lambda':
                  target_name="lambda"
              elif tg_dict.get('TargetType') == 'alb':
                  target_name="alb"
              # TargetHealth State: initial'|'healthy'|'unhealthy'|'unused'|'draining'|'unavailable'
              if target_state == 'healthy':
                  target_state = "[green]"+target_state
              elif target_state == 'unhealthy':
                  target_state = "[red]"+target_state
              else:
                  target_state = "[orange1]"+target_state
              tg_branch.add("[cyan]"+target_id+" [white]("+target_name+") [white]Status: "+str(target_state)+" [white]Description: "+str(target_state_desc))
    print(tree)

def main():
    parser = argparse.ArgumentParser(description='For every Elastic Load Balancer list the attached instances')
    parser.add_argument('-t', '--type', choices=['classic', 'current', 'all'],
                        default="all", help="It shows the current generation of ELBs (Application, Network and/or Gateway) and/or the previous one (Classic).")

    arg = parser.parse_args()
    
    session = boto3.session.Session()
    region = session.region_name

    ec2 = boto3.resource('ec2')
    if arg.type == 'classic' or arg.type == 'all':
        list_elb(ec2, region)
    if arg.type == 'current' or arg.type == 'all':
        list_elbv2(ec2, region)

if __name__ == '__main__':
    sys.exit(main())
