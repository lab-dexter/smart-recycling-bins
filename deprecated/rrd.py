#!/usr/bin/python
#
# This script takes 2 arguments:
#   - sample count to feed into the database
#   - sample step seconds
#
# Example usage can be found in main() function
#
#
# Documentation:
# https://oss.oetiker.ch/rrdtool/tut/rrd-beginners.en.html
# https://oss.oetiker.ch/rrdtool/tut/rrdtutorial.en.html
# http://cuddletech.com/articles/rrd/ar01s02.html
# https://supportex.net/blog/2011/09/rrd-python/
# https://notroot.wordpress.com/2010/03/22/python-rrdtool-tutorial/
#

import sys
import rrdtool
from rrdtool import update as rrd_update
from rrdtool import fetch as rrd_fetch
import random
import time
import datetime

# Simple command line arg parsing
def parse_arg():
  print '--------------------------------------'
  print 'Number of arguments:', len(sys.argv), 'arguments.'
  print 'Argument List:', str(sys.argv)
  print '--------------------------------------'
  sample_cnt = sys.argv[1]
  sample_step_sec = sys.argv[2]

  # Global var for fake_data_write and update_db functions
  global db_name 
  db_name = 'example.rrd'

  print '--------------------------------------'
  print 'Database name: ', db_name
  print 'Sample count: ', sample_cnt
  print 'Database sample step seconds: ', sample_step_sec
  print '--------------------------------------'
  return db_name, sample_cnt, sample_step_sec

def rrd_create(db_name, sample_step_sec):
  ret = rrdtool.create(db_name, "--step", sample_step_sec, "--start", '0',
    "DS:metric1:GAUGE:4:U:U",
    "DS:metric2:GAUGE:4:U:U",
    "DS:metric3:GAUGE:4:U:U",
    "DS:metric4:GAUGE:4:U:U",
    "RRA:AVERAGE:0.5:1:600",
    "RRA:MAX:0.5:1:600")
 
# Basic function to write new values at the specified timestamp
def update_db(timestamp, metric1, metric2, metric3, metric4):
  ret = rrd_update(db_name, '%s:%s:%s:%s:%s' % (timestamp, metric1, metric2, metric3, metric4));
  print "%s: Updated db @%s with: %s, %s, %s, %s" % (datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'), timestamp, metric1, metric2, metric3, metric4)

# This is an example wrapper function to demonstrate 
# how we can write some values to rrd over time
def fake_data_write(sample_count, sample_db_step):
  start_end_times = {}
  sample_count = int(sample_count)
  for sample in range(sample_count):
    # 4 random metrics
    sensor1_val = random.randint(1,10)
    sensor2_val = sensor1_val + 3
    sensor3_val = sensor1_val + 6
    sensor4_val = sensor1_val + 9
    
    timestamp = int(time.time())
    update_db(timestamp, sensor1_val, sensor2_val, sensor3_val, sensor4_val)
    # Storing time range in dict in order to retrieve later
    if sample == 0:
      start_end_times['start'] = timestamp
    elif sample == (sample_count - 1):
      start_end_times['end'] = timestamp
    time.sleep(int(sample_db_step))

  print start_end_times
  return start_end_times

# Retrieves data from the specified time frame.
# db - database file name
# time_frame - dict with start, end items, e.g.: {'start': 1511116898, 'end': 1511116902}
#
# Data fetch example cmdline:
# rrdtool fetch example.rrd LAST --start 1510487244 --end 1510487260
def fetch_db(db, time_frame):
  start_sec = time_frame.get('start')
  end_sec = time_frame.get('end')
  print "Fetching from \'%s\' db. Start: %s ; End: %s" % (str(db), start_sec, end_sec)
  data = rrd_fetch(db, 'AVERAGE', '--start', str(start_sec), '--end', str(end_sec))
  print data
  return data

# Example usage
def main():
  db_name, sample_cnt, sample_step_sec = parse_arg()
  rrd_create(db_name, sample_step_sec)
  time_frame = fake_data_write(sample_cnt, sample_step_sec)
  fetch_db(db_name, time_frame)

if __name__ == "__main__":
    main()
