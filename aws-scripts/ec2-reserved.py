#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
from datetime import date, datetime, timedelta
import hashlib
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import argparse

def list_reserved_instances(filters):
    events = []
    instances = []
    event_ids = []
    client = boto3.client('ec2')
    response = client.describe_reserved_instances(Filters=filters)
    size = len(response.get('ReservedInstances'))
    columns_format="%-36s %-10s %-12s %-24s %-18s %-14s %-10s %-9s %-26s %-6s"
    print(columns_format % ("Reserved Id", "Instances", "Type", "Product Description", "Scope", "Zone", "Duration", "Time Left", "End", "Offering"))
    for n in range(size):
        id = response.get('ReservedInstances')[n].get('ReservedInstancesId')
        count = response.get('ReservedInstances')[n].get('InstanceCount')
        type = response.get('ReservedInstances')[n].get('InstanceType')
        product = response.get('ReservedInstances')[n].get('ProductDescription')
        scope = response.get('ReservedInstances')[n].get('Scope')
        zone = response.get('ReservedInstances')[n].get('AvailabilityZone')
        duration = response.get('ReservedInstances')[n].get('Duration')
        offering = response.get('ReservedInstances')[n].get('OfferingType')
        td = timedelta(seconds=int(duration))
        end = response.get('ReservedInstances')[n].get('End')
        end_dt = datetime.strptime(str(end), "%Y-%m-%d %H:%M:%S+00:00")
        now_dt = datetime.now()
        delta = end_dt - now_dt
        time_left = max(0, delta.days)
        print(columns_format % (id, count, type, product, scope, zone, td.days, time_left, end, offering))
        description="A purchased reservervation affecting to %s x %s instances is about to expire. Reservation id: %s" % (count, type, id)
    
        if time_left > 0:
            state = 'active'
        else:
            state = 'retired'
        
        instance = {
                    'scope': scope, 
                    'zone': zone,
                    'type': type,
                    'state': state,
                    'count': count
        }
        instances.append(instance)
        
        event_start = end_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        event_end = (end_dt + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        m = hashlib.sha224()
        m.update(id.encode())
        sha_id = m.hexdigest()
        event = {
          'id': sha_id,
          'summary': 'Reserve Instance Expiration',
          'location': 'aws',
          'description': description,
          'start': {
            'dateTime': event_start,
            'timeZone': 'America/Los_Angeles',
          },
          'end': {
            'dateTime': event_end,
            'timeZone': 'America/Los_Angeles',
          },
          'reminders': {
            'useDefault': False,
            'overrides': [
              {'method': 'email', 'minutes': 24 * 60},
              {'method': 'popup', 'minutes': 10},
            ],
          },
        }
        events.append(event)
        event_ids.append(sha_id)
    
    return events, event_ids, instances

def create_events(service, events, event_ids):
    import datetime
    
    page_token = None
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        if calendar_list_entry['summary'] == "aws":
            calendar_id = calendar_list_entry['id']
            
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break
    
    ''' Get the current events from Google Calendar'''
    page_token = None
    g_event_ids = []
    while True:
      g_events = service.events().list(calendarId=calendar_id, pageToken=page_token).execute()
      for event in g_events['items']:
        g_event_ids.append(event['id'])
      page_token = g_events.get('nextPageToken')
      if not page_token:
        break
    
    if len(events) >= 1:
        print("Creating %s events in the aws Calendar of your Google Account" % len(events))
    
    n=0
    for id in event_ids :
        if id in g_event_ids:
            print("The event: %s is already scheduled. Nothing to do..." % events[n]['id'])
        else:
            event = service.events().insert(calendarId=calendar_id, body=events[n]).execute()
            print("Event created: %s" % event.get('htmlLink'))
        n += 1



def main():
    parser = argparse.ArgumentParser(description='Show reserved EC2 instances')
    parser.add_argument('-s', '--state', action='store',
                        choices=['payment-pending', 'active', 'payment-failed', 'retired'],
                        help="Filer result by reservation state.")
    parser.add_argument('--create-google-calendar-events',
                        action='store_true',
                        default=False,
                        help="Create events in your Google Calendar, using the \
                              expiration dates of your active reservations")
    parser.add_argument('-t', '--type',
                        help="Filer result by instance type.")

    arg = parser.parse_args()

    filters=[]

    if arg.create_google_calendar_events:
        filters=[]
        filters.append({'Name': 'state', 'Values': ['active']})

    if arg.state and arg.create_google_calendar_events is False:
        filters.append({'Name': 'state', 'Values': ["" + arg.state + ""]})

    if arg.type and arg.create_google_calendar_events is False:
        filters.append({'Name': 'instance-type', 'Values': ["*" + arg.type + "*"]})

    events, event_ids, instances = list_reserved_instances(filters)

    normalization_factor = {
        'nano': 0.25,
        'micro': 0.5,
        'small': 1,
        'medium': 2,
        'large': 4,
        'xlarge': 8,
        '2xlarge': 16,
        '4xlarge': 32,
        '8xlarge': 64,
        '9xlarge': 72,
        '10xlarge': 80,
        '12xlarge': 96,
        '16xlarge': 128,
        '18xlarge': 144,
        '24xlarge': 192,
        '32xlarge': 256
    }
    
    # Normalized value for regional and zonal active reservations
    region  = {}
    zone = {}
    for instance in instances:
        instance_type, instance_size = instance['type'].split('.')
        if instance['state']  == 'active':
            if instance['scope'] == 'Region':
                if instance_type not in region:
                    region[instance_type] = { instance_size: instance['count']}
                elif instance_size in region[instance_type]:
                        region[instance_type][instance_size] += instance['count']
                else:
                    region[instance_type][instance_size] = instance['count']
            elif instance['scope'] == 'Availability Zone':
                if instance_type not in zone:
                    zone[instance_type] = {}
                    zone[instance_type][instance['zone']] = {}
                    zone[instance_type][instance['zone']] = { instance_size: instance['count'] }
                elif instance_size in zone[instance_type][instance['zone']]:
                    zone[instance_type][instance['zone']][instance_size] += instance['count']
                else:
                    zone[instance_type][instance['zone']][instance_size] = instance['count']
    
    nrrs = 0    
    nrrs_sum = 0
    print("")
    print("Summary")
    print("")
    print("  Active Standard Regional Reserverd Instances (by type and size)")
    for type in region:
        print("    Instance Type: %s" % type)
        nrrs += nrrs
        for size in region[type]:
          # Normalized reserved region size (nrrs)
          nrrs = normalization_factor[size] * region[type][size]
          nrrs_sum = nrrs_sum + nrrs
          print("      %s x %s (%s) = %s" % (region[type][size], size, normalization_factor[size], nrrs))
    
    print("")
    print("  Total Regional (normalized): %s" % nrrs_sum)
    print("")
    print("")
    
    nrrs = 0    
    nrrs_sum = 0
    print("  Active Standard Zonal Reserverd Instances (by type, availability zone and size)")
    for type in zone:
        print("    Instance Type: %s" % type)
        nrrs += nrrs
        for availability_zone in zone[type]:
          print("      Availabilidy zone: %s" % availability_zone)
          for size in zone[type][availability_zone]:
              nrrs = normalization_factor[size] * zone[type][availability_zone][size]
              nrrs_sum = nrrs_sum + nrrs
              print("        %s x %s (%s) = %s" % (zone[type][availability_zone][size], size, normalization_factor[size], nrrs))
    
    print("")
    print("  Total Zonal (normalized): %s" % nrrs_sum)
    print("")
    
    
    if arg.create_google_calendar_events:
        # Setup the Calendar API
        SCOPES = 'https://www.googleapis.com/auth/calendar'
        store = file.Storage('credentials.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
            flags = tools.argparser.parse_args(args=[])
            creds = tools.run_flow(flow, store, flags)
        service = build('calendar', 'v3', http=creds.authorize(Http()))
        create_events(service, events, event_ids)

if __name__ == '__main__':
    sys.exit(main())
