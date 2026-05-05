#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
import argparse
from rich.tree import Tree
from rich import print
from rich.progress import track

def get_instance_info_batch(ec2, instance_ids):
    if not instance_ids:
        return {}
    instances = ec2.instances.filter(InstanceIds=instance_ids)
    info = {}
    for instance in instances:
        name = ""
        if instance.tags:
            for tag in instance.tags:
                if tag.get('Key') == 'Name':
                    name = tag.get('Value', '')
                    break
        info[instance.id] = {
            'name': name,
            'zone': instance.placement.get('AvailabilityZone', '')
        }
    return info

def list_elb(ec2, region):
    client = boto3.client('elb')
    response = client.describe_load_balancers()
    tree = Tree("[bold white]Classic Elastic Load Balancers in the "+region+" AWS region")

    all_instance_ids = []
    for elb_desc in response.get('LoadBalancerDescriptions', []):
        for instance in elb_desc.get('Instances', []):
            all_instance_ids.append(instance.get('InstanceId'))

    instance_info = get_instance_info_batch(ec2, all_instance_ids)

    for elb in track(range(len(response.get('LoadBalancerDescriptions'))), description="Processing..."):
        elb_desc = response.get('LoadBalancerDescriptions')[elb]
        load_balancer_name = elb_desc.get('LoadBalancerName')
        elb_instances = elb_desc.get('Instances', [])

        elb_health = client.describe_instance_health(LoadBalancerName=load_balancer_name)
        health_by_id = {s.get('InstanceId'): s.get('State') for s in elb_health.get('InstanceStates', [])}

        elb_tree = tree.add(":file_folder: [bold white]"+load_balancer_name)
        instances_info = []

        for instance in elb_instances:
            instance_id = instance.get('InstanceId')
            info = instance_info.get(instance_id, {'name': '', 'zone': ''})
            instance_state = health_by_id.get(instance_id, 'Unknown')
            instances_info.append({
                "id": instance_id,
                "name": info.get('name', ''),
                "zone": info.get('zone', ''),
                "state": instance_state
            })

        for zone in elb_desc.get('AvailabilityZones', []):
            zone_name = zone
            zone_tree = elb_tree.add(":file_folder: [bold white]"+zone_name)
            for inst in instances_info:
                if inst.get('zone') == zone_name:
                    if inst.get('state') == 'OutOfService':
                        branch = zone_tree.add("[cyan]"+inst.get('id')+" [white]("+inst.get('name')+")"+" Status: [red]"+inst.get('state'))
                    else:
                        branch = zone_tree.add("[cyan]"+inst.get('id')+" [white]("+inst.get('name')+")"+" Status: [green]"+inst.get('state'))
    print(tree)

def list_elbv2(ec2, region):
    client = boto3.client('elbv2')
    response = client.describe_load_balancers()
    tree = Tree("[bold white]Current Generation of Elastic Load Balancers in %s AWS region" % region)

    all_target_ids = []
    elbs_data = []

    for elb in response.get('LoadBalancers', []):
        load_balancer_arn = elb.get('LoadBalancerArn')
        load_balancer_name = elb.get('LoadBalancerName')
        load_balancer_type = elb.get('Type')
        load_balancer_zones = elb.get('AvailabilityZones', [])

        tg_response = client.describe_target_groups(LoadBalancerArn=load_balancer_arn)
        tgs_data = []

        for tg in tg_response.get('TargetGroups', []):
            tg_arn = tg.get('TargetGroupArn')
            tg_name = tg.get('TargetGroupName')
            tg_type = tg.get('TargetType')

            health_response = client.describe_target_health(TargetGroupArn=tg_arn)
            targets_data = []

            for th in health_response.get('TargetHealthDescriptions', []):
                target_id = th.get('Target', {}).get('Id', '')
                target_state = th.get('TargetHealth', {}).get('State', 'unknown')
                target_desc = th.get('TargetHealth', {}).get('Description', '')

                if tg_type == 'instance' and target_id:
                    all_target_ids.append(target_id)
                    targets_data.append({
                        'id': target_id,
                        'type': tg_type,
                        'state': target_state,
                        'desc': target_desc
                    })
                elif tg_type == 'ip':
                    targets_data.append({'id': target_id, 'type': 'ip', 'state': target_state, 'desc': target_desc})
                elif tg_type == 'lambda':
                    targets_data.append({'id': target_id, 'type': 'lambda', 'state': target_state, 'desc': target_desc})
                elif tg_type == 'alb':
                    targets_data.append({'id': target_id, 'type': 'alb', 'state': target_state, 'desc': target_desc})

            tgs_data.append({
                'name': tg_name,
                'type': tg_type,
                'targets': targets_data
            })

        elbs_data.append({
            'name': load_balancer_name,
            'type': load_balancer_type,
            'zones': load_balancer_zones,
            'target_groups': tgs_data
        })

    instance_info = get_instance_info_batch(ec2, all_target_ids)

    for elb_data in track(elbs_data, description="Processing..."):
        elb_branch = tree.add(":file_folder:[bold white] "+elb_data['name']+" Type: "+elb_data['type'])
        tg_folder = elb_branch.add(":file_folder: Target Groups")

        for tg in elb_data['target_groups']:
            tg_branch = tg_folder.add(":file_folder:[bold white] "+tg['name']+" [not bold]Type: "+tg['type'])

            for zone in elb_data['zones']:
                zone_name = zone.get('ZoneName', '')
                zone_tree = tg_branch.add(":file_folder: [white]"+zone_name)

                for target in tg['targets']:
                    if target['type'] != 'instance':
                        target_name = target['type']
                        target_zone = ''
                    else:
                        target_id = target['id']
                        info = instance_info.get(target_id, {'name': '', 'zone': ''})
                        target_name = info.get('name', '')
                        target_zone = info.get('zone', '')

                    target_state = target['state']
                    target_desc = target['desc']

                    if target_state == 'healthy':
                        target_state_colored = "[green]"+target_state
                    elif target_state == 'unhealthy':
                        target_state_colored = "[red]"+target_state
                    else:
                        target_state_colored = "[orange1]"+target_state

                    if target.get('type') == 'instance' and target_zone == zone_name:
                        zone_tree.add("[cyan]"+target['id']+" [white]("+target_name+") [white]Status: "+target_state_colored+" [white]Description: "+str(target_desc))
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