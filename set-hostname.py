#!/usr/bin/env python
import sys
import argparse
import boto3
import re
import urllib2

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
    response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/public-hostname')
    public_dns = response.read()
    print "Public DNS hostname: %s" % public_dns
    return public_dns

def get_local_dns_hostname():
    # curl http://169.254.169.254/latest/meta-data/hostname
    response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/hostname')
    local_dns = response.read()
    print "Local DNS hostname: %s" % local_dns
    return local_dns

def get_private_ip():
    # curl http://169.254.169.254/latest/meta-data/local-ipv4
    response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4')
    private_ip = response.read()
    print "Private IP: %s" % private_ip
    return private_ip

def get_public_ip():
    # curl http://169.254.169.254/latest/meta-data/public-ipv4
    response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/public-ipv4')
    public_ip = response.read()
    print "Public IP: %s" % public_ip
    return public_ip

def set_hostname_record():
    # Set hostname in Route53
    print hola

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

    if arg.dryrun:
       print "First available hostname in the range: %s" % available_hostname

    #get_private_ip()
    #get_public_dns_hostname()
    #get_local_dns_hostname()
    #get_public_ip()

if __name__ == '__main__':
    sys.exit(main())
