#!/usr/bin/python

import re
import os
import sys
import getpass
import urllib2

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        json = None


def login():
    try :
        print "First, please login using your RapidSpike credentials."

        email = raw_input("\tEnter your email: ")
        password = getpass.getpass("\tEnter your password: ")

        req = urllib2.Request('https://api.rapidspike.com/v1/users/login')
        req.add_header('Content-Type', 'application/json')

        res_raw = urllib2.urlopen(req, json.dumps({'email': email, 'password': password}))
        res_data = json.load(res_raw)

        # Everything went ok, so return the auth token
        return res_data['data']['auth']['token']
    except urllib2.HTTPError, err:
        if err.code == 400:
            print "\nInvalid credentials!"
        else:
            print "Something happened! Error code", err.code
    except urllib2.URLError, err:
        print "Some other error happened:", err.reason

    # The login must have failed, so exit!
    sys.exit()


def delete_rca(auth_token, monitor_data):
    try:
        req = urllib2.Request('https://api.rapidspike.com/v1/rcamonitors/' + monitor_uuid)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', 'Bearer ' + auth_token)
        req.get_method = lambda: "DELETE"

        res_raw = urllib2.urlopen(req, json.dumps(monitor_data))
        res_data = json.load(res_raw)

        print "\nThe RCA monitor has been deleted from your account."
        return res_data
    except urllib2.HTTPError, err:
        print "Something happened! Error code", err.code
    except urllib2.URLError, err:
        print "Some other error happened:", err.reason

    # The API call must have failed, so exit!
    print "Please check the account your authenticated with owns the monitor."
    sys.exit()


print "================================================================="
print "          ____              _     _______       _ __       "
print "         / __ \____ _____  (_)___/ / ___/____  (_) /_____  "
print "        / /_/ / __ `/ __ \/ / __  /\__ \/ __ \/ / //_/ _ \ "
print "       / _, _/ /_/ / /_/ / / /_/ /___/ / /_/ / / ,< /  __/ "
print "      /_/ |_|\__,_/ .___/_/\__,_//____/ .___/_/_/|_|\___/  "
print "                 /_/                 /_/                   "
print "    ___  ________     __  __     _          __       ____        "
print "   / _ \/ ___/ _ |   / / / /__  (_)__  ___ / /____ _/ / /__ ____ "
print "  / , _/ /__/ __ |  / /_/ / _ \/ / _ \(_-</ __/ _ `/ / / -_) __/ "
print " /_/|_|\___/_/ |_|  \____/_//_/_/_//_/___/\__/\_,_/_/_/\__/_/    "
print "================================================================="
print "\nWelcome to the RapidSpike RCA uninstaller!"

file_path = 'config/run_list.json'
with open(file_path) as run_list_file:    
    run_list = json.load(run_list_file)

if len(run_list) == 0:
    print "There are no scripts installed and configured!"
    sys.exit()

print "Scripts installed and configured:"
i = 0
l = []
for run_item in run_list:
    i = i + 1
    print "\t[" + str(i) + "] " + run_item['script']

req_script = raw_input("\nWhich script would you like to uninstall? ")
req_script_id = int(req_script) - 1
script_name = run_list[req_script_id]['script']

sure = raw_input("Are you sure you wish to uninstall '" + script_name + "'? (y/n) ")
if sure == 'y':
    auth_token = login()
    monitor_uuid = run_list[req_script_id]['monitor_uuid']
    delete_rca(auth_token, monitor_uuid)

    del run_list[req_script_id]
    f = open(file_path, 'w')
    f.write(json.dumps(run_list))
    f.close()
    print "\n'" + script_name + "' has been uninstalled successfully."

print "================================================================="
print "      ______ __                   __      __  __              "
print "     /_  __// /_   ____ _ ____   / /__    \ \/ /____   __  __ "
print "      / /  / __ \ / __ `// __ \ / //_/     \  // __ \ / / / / "
print "     / /  / / / // /_/ // / / // ,<        / // /_/ // /_/ /  "
print "    /_/  /_/ /_/ \__,_//_/ /_//_/|_|      /_/ \____/ \__,_/   "
print "================================================================="