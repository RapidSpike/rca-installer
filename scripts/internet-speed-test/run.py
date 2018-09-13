#!/usr/bin/python

import os
import urllib2
import subprocess
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


def run_speed_test(cur_dir):
    try:
        response = subprocess.check_output(
            [cur_dir + '/vendor/speedtest-cli', '--json'],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        return json.loads(response)
    except subprocess.CalledProcessError:
        return None


def send_data(id, ping, download, upload):
    query = urlencode(OrderedDict(id=id, ping=ping, download=download, upload=upload))
    res_raw = urllib2.urlopen('https://results.rapidspike.com/rca?' + query)
    return res_raw.read()


cur_dir = os.path.dirname(os.path.realpath(__file__))
monitor_uuid = get_uuid(cur_dir)
test_data = run_speed_test(cur_dir)

ping = round(float(test_data['ping']), 2)
download = round(float(test_data['download']) / 1048576, 2)
upload = round(float(test_data['upload']) / 1048576, 2)

response = send_data(monitor_uuid, ping, download, upload)