#!/usr/bin/env python
import sys
import argparse
import boto3
import re
try:
    import urllib2
except ImportError:
    import urllib.request, urllib.error, urllib.parse
import time
from datetime import datetime

def get_available_hostname(HostedZoneId, HostStr, rangeSize):

    client = boto3.client('route53')

    # Getting domain por the provided HostedZoneId
    zones = client.list_hosted_zones()
    for zone in range(len(zones.get('HostedZones'))):
       zoneid = zones.get('HostedZones')[zone].get('Id')
       regex = r"/hostedzone/" + re.escape(HostedZoneId)
       Idzone = re.match(regex,zoneid)
       if Idzone:
          domain = zones.get('HostedZones')[zone].get('Name')

    # Getting first available index in the provided range
    response = client.list_resource_record_sets(HostedZoneId=HostedZoneId)
    num_found = 0
    l = [None] * rangeSize
    # Fill the list with founded value using the number as index
    # Unasigned indexes will appear as None
    for record in range(len(response.get('ResourceRecordSets'))):
       name = response.get('ResourceRecordSets')[record].get('Name')
       regex = r"(" + re.escape(HostStr) + ")(\d+).*"
       host=re.match(regex, name)
       if host:
          num_found=int(host.group(2))
          hostname=host.group(0)
          l[num_found]=hostname;

    # Getting first free index
    n = 0
    while l[n] is not None:
       n = n + 1

    hostname = "%s%02d.%s" % (HostStr,n,domain)
    return hostname

def get_public_dns_hostname():
    # curl http://169.254.169.254/latest/meta-data/public-hostname
    try:
        # if python 2.x
        response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/public-hostname')
    except:
        # if python3.x
        response = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/public-hostname')
    public_dns = response.read()
    return public_dns

def get_local_dns_hostname():
    # curl http://169.254.169.254/latest/meta-data/hostname
    try:
        # if python 2.x
        response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/hostname')
    except:
        # if python 3.x
        response = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/hostname')
    local_dns = response.read()
    return local_dns

def get_private_ip():
    # curl http://169.254.169.254/latest/meta-data/local-ipv4
    try:
        # if python 2.x
        response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4')
    except:
        # if python 3.x
        response = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4')
    private_ip = response.read()
    return private_ip

def get_public_ip():
    # curl http://169.254.169.254/latest/meta-data/public-ipv4
    try:
        # if python 2.x    
        response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/public-ipv4')
    except:
       response = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/public-ipv4')
    public_ip = response.read()
    return public_ip

def set_hostname_record(HostedZoneId, public_dns, available_hostname, private_ip):
    # Set hostname in Route53
    client = boto3.client('route53')
    response = client.change_resource_record_sets(
    HostedZoneId=HostedZoneId,
    ChangeBatch={
    "Comment": "Record added using set-hostname.py script. From: " + private_ip,
    "Changes": [
        {
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": available_hostname,
                "Type": "CNAME",
                "TTL": 300,
                "ResourceRecords": [
                    {
                        "Value": public_dns
                    },
                ]
            }
         },
       ]
     }
    )
    idstring = response.get('ChangeInfo').get('Id')
    response = client.get_change(Id=idstring)
    while response.get('ChangeInfo').get('Status') == 'PENDING':
       sys.stdout.write('.')
       sys.stdout.flush()
       time.sleep( 5 )
       response = client.get_change(Id=idstring)
    else:
       print(response.get('ChangeInfo').get('Status'))
       return

def main():
    parser = argparse.ArgumentParser(description='AWS Route53 hostname managment for Autoscaled EC2 Instances')
    parser.add_argument('--HostedZoneId', required=True,
                        help="The ID of the hosted zone where the new resource record will be added.")
    parser.add_argument('--HostStr', required=True,
                        help="The host string used to build the new name")
    parser.add_argument('--rangeSize', type=int, default=10,
                        help="The maximun number to be assigned. The first available will be used" )
    parser.add_argument('--dryrun', action='store_true',
                        help="Shows what is going to be done but doesn't change anything actually")

    arg = parser.parse_args()

    available_hostname = get_available_hostname(arg.HostedZoneId, arg.HostStr, arg.rangeSize)

    private_ip = get_private_ip()
    public_dns = get_public_dns_hostname()
    #get_local_dns_hostname()
    #get_public_ip()
    date = datetime.now().strftime('%H:%M:%S %D')
    sys.stdout.write ("%s: creating CNAME %s -> %s" % (date, available_hostname, public_dns))
    sys.stdout.flush()

    if arg.dryrun is False:
       set_hostname_record(arg.HostedZoneId, public_dns, available_hostname, private_ip)

if __name__ == '__main__':
    sys.exit(main())
