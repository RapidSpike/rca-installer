#!/usr/bin/python
 
import os
import psutil
import urllib2
from urllib import urlencode, quote
from collections import OrderedDict

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        json = None


def get_uuid(cur_dir):
    with open(cur_dir + '/config.json') as config_file:    
        config = json.load(config_file)
    return config['uuid']


def send_data(id, load_avg_1, load_avg_5, load_avg_15, cpu, mem):
    query = urlencode(OrderedDict(id=id, loadavg1=load_avg_1, loadavg5=load_avg_5, loadavg15=load_avg_15, cpu=cpu, memory=mem))
    res_raw = urllib2.urlopen('https://results.rapidspike.com/rca?' + query)
    return res_raw.read()


cur_dir = os.path.dirname(os.path.realpath(__file__))
monitor_uuid = get_uuid(cur_dir)

load_avgs = os.getloadavg()
load_avg_1 = round(load_avgs[0], 2)
load_avg_5 = round(load_avgs[1], 2)
load_avg_15 = round(load_avgs[2], 2)

cpu = psutil.cpu_percent()

mem = psutil.virtual_memory().percent

response = send_data(monitor_uuid, load_avg_1, load_avg_5, load_avg_15, cpu, mem)