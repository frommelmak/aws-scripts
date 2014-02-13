#!/usr/bin/env python
import sys
import boto.ec2
import argparse

# List all the snapshots for every volume
def snap_x_vol(owner_id):
    conn = boto.ec2.connection.EC2Connection()
    snapshots = conn.get_all_snapshots(owner=owner_id)
    volumes = conn.get_all_volumes()
    for v in volumes:
        print "- %s" % (v.id)
        for s in snapshots:
            if s.volume_id == v.id:
                print "   \_ %s, start_time: %s" % (s.id, s.start_time)

# Find orphan snapshots (snapshots of non-existeng volumnes and snapshots without ami)
def orphan_snapshots(owner_id):
    conn = boto.ec2.connection.EC2Connection()
    snapshots = conn.get_all_snapshots(owner=owner_id)
    volumes = conn.get_all_volumes()
    images = conn.get_all_images(owners=owner_id)
    for s in snapshots:
        print "- %s" % (s.id)
        for v in volumes:
            if s.volume_id == v.id:
                print "   \_(volume %s)" % (v.id)
        for i in images:
            for dev in i.block_device_mapping:
                if s.id == i.block_device_mapping[dev].snapshot_id:
                    print "   \_(ami %s) %s" % (i.id, dev)
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--view', default='orphan', choices=['orphan', 'volumes'],
                        help="Available views: orphan and volumes. Orphan is the default one.")
    parser.add_argument('owner_id', help="12-digit AWS Account Number")
    arg = parser.parse_args()

    if arg.view == 'orphan':
        orphan_snapshots(arg.owner_id)

    if arg.view == 'volumes':
        snap_x_vol(arg.owner_id)

if __name__ == '__main__':
    sys.exit(main())
