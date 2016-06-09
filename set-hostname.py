#!/usr/bin/env python
import sys
import argparse
import boto3
import re

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

def main():
    parser = argparse.ArgumentParser(description='bla bla')
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

if __name__ == '__main__':
    sys.exit(main())
