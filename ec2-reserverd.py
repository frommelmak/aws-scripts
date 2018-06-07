#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
import argparse
from datetime import date, datetime, timedelta
import hashlib

def list_reserved_instances(ec2, filters):
    events = []
    event_ids = []
    client = boto3.client('ec2')
    response = client.describe_reserved_instances(Filters=filters)
    size = len(response.get('ReservedInstances'))
    columns_format="%-36s %-10s %-12s %-24s %-18s %-14s %-10s %-9s %-26s %-6s"
    print columns_format % ("Reserved Id", "Instances", "Type", "Product Description", "Scope", "Region", "Duration", "Time Left", "End", "Offering")
    for n in range(size):
        id = response.get('ReservedInstances')[n].get('ReservedInstancesId')
        count = response.get('ReservedInstances')[n].get('InstanceCount')
        type = response.get('ReservedInstances')[n].get('InstanceType')
        product = response.get('ReservedInstances')[n].get('ProductDescription')
        scope = response.get('ReservedInstances')[n].get('Scope')
        region = response.get('ReservedInstances')[n].get('AvailabilityZone')
        duration = response.get('ReservedInstances')[n].get('Duration')
        offering = response.get('ReservedInstances')[n].get('OfferingType')
        td = timedelta(seconds=int(duration))
        end = response.get('ReservedInstances')[n].get('End')
        end_dt = datetime.strptime(str(end), "%Y-%m-%d %H:%M:%S+00:00")
        now_dt = datetime.now()
        delta = end_dt - now_dt
        print columns_format % (id, count, type, product, scope, region, td.days, max(0, delta.days), end, offering)
        description="A purchased reservervation affecting to %s x %s instances is about to expire. Reservation id: %s" % (count, type, id)
        
        event_start = end_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        event_end = (end_dt + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        m = hashlib.sha224()
        m.update(id)
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
    
    return events, event_ids

def create_google_calendar_events(events, event_ids):
    from apiclient.discovery import build
    from httplib2 import Http
    from oauth2client import file, client, tools
    import datetime

    # Setup the Calendar API
    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

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
        print "Creating %s events in the aws Calendar of your Google Account" % len(events)
    
    n=0
    for id in event_ids :
        if id in g_event_ids:
            print "The event: %s is already scheduled. Nothing to do..." % events[n]['id']
        else:
            event = service.events().insert(calendarId=calendar_id, body=events[n]).execute()
            print "Event created: %s" % event.get('htmlLink')
        n += 1



def main():
    parser = argparse.ArgumentParser(description='Show active reserved EC2 instances')
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

    ec2 = boto3.resource('ec2')
    events, event_ids = list_reserved_instances(ec2, filters)
    
    if arg.create_google_calendar_events:
        create_google_calendar_events(events, event_ids)    

if __name__ == '__main__':
    sys.exit(main())
