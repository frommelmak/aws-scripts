#!/usr/bin/env python
import sys
import argparse
import boto3
try:
    import urllib2
except ImportError:
    import urllib.request, urllib.error, urllib.parse
import time
from datetime import datetime
import socket

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

def get_private_ip():
    # curl http://169.254.169.254/latest/meta-data/local-ipv4
    try:
        # if python 2.x
        response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4')
    except:
        response = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4')
    
    private_ip = response.read()
    return private_ip

def del_hostname_record(HostedZoneId, public_dns, fqdn, private_ip):
    # Delete hostname from Route53
    client = boto3.client('route53')
    response = client.change_resource_record_sets(
    HostedZoneId=HostedZoneId,
    ChangeBatch={
    "Comment": "Record deleted using route53-del-hostname.py script. From: " + private_ip,
    "Changes": [
        {
            "Action": "DELETE",
            "ResourceRecordSet": {
                "Name": fqdn,
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
    parser = argparse.ArgumentParser(description='Delete host record from AWS Route53 zone')
    parser.add_argument('--HostedZoneId', required=True,
                        help="The ID of the hosted zone where the new resource record will be added.")
    parser.add_argument('--dryrun', action='store_true',
                        help="Shows what is going to be done but doesn't change anything actually")

    arg = parser.parse_args()

    hostname=socket.gethostname()

    private_ip = get_private_ip()
    public_dns = get_public_dns_hostname()

    client = boto3.client('route53')
    zone = client.get_hosted_zone(Id=arg.HostedZoneId)
    fqdn = hostname+'.'+zone['HostedZone']['Name']
    date = datetime.now().strftime('%H:%M:%S %D')
    sys.stdout.write ("%s: deleting CNAME %s -> %s" % (date, fqdn, public_dns))
    sys.stdout.flush()

    if arg.dryrun is False:
       del_hostname_record(arg.HostedZoneId, public_dns, fqdn, private_ip)

if __name__ == '__main__':
    sys.exit(main())
