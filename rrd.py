#!/usr/bin/python
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
import random
import time
import datetime

print '--------------------------------------'
print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)
print '--------------------------------------'
sample_cnt = sys.argv[1]
sample_step_sec = sys.argv[2]

print '--------------------------------------'
print 'Sample count: ', sample_cnt
print 'Database sample step seconds: ', sample_step_sec
print '--------------------------------------'

ret = rrdtool.create("example.rrd", "--step", sample_step_sec, "--start", '0',
  "DS:metric1:GAUGE:4:U:U",
  "DS:metric2:GAUGE:4:U:U",
  "RRA:AVERAGE:0.5:1:600",
  "RRA:MAX:0.5:1:600")

# Basic function to write new values at the specified timestamp
def update_db(timestamp, metric1, metric2):
  ret = rrd_update('example.rrd', '%s:%s:%s' % (timestamp, metric1, metric2));
  print "%s: Updated db @%s with: %s, %s" % (datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'), timestamp, metric1, metric2)

# Dummy loop to write 2 random metrics
def fake_data_write(sample_count, sample_db_step):
  start_end_times = {}
  sample_count = int(sample_count)
  for sample in range(sample_count):
    # Two random metrics
    metric1 = random.randint(1,10)
    metric2 = metric1 + 3
    
    timestamp = int(time.time())
    update_db(timestamp, metric1, metric2)
    # Storing time range in dict in order to retrieve later
    if sample == 0:
      start_end_times['start'] = timestamp
    elif sample == (sample_count - 1):
      start_end_times['end'] = timestamp
    time.sleep(int(sample_db_step))

  print start_end_times

fake_data_write(sample_cnt, sample_step_sec)
# Data fetch example cmdline:
# rrdtool fetch example.rrd LAST --start 1510487244 --end 1510487260
