#!/usr/bin/python

import re
import os
import sys
import getpass
import urllib2
import subprocess

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


def request_script():
    print "\nScripts available for setup:"

    i = 0
    l = []
    script_dirs = os.listdir("scripts")

    for dir_name in script_dirs:
        if dir_name[0] != '.':
            i = i + 1
            l.append(dir_name)
            print "\t[" + str(i) + "] " + dir_name

    script_id = raw_input("Which script would you like to setup? ")
    script_name = l[int(script_id) - 1]

    print "You selected to setup '" + script_name + "'"
    return script_name


# def request_keys():
#     a = []
#     while True:
#         label = raw_input("\tEnter a label: ")
#         key_name = raw_input("\tEnter a key name: ")
#         metric = raw_input("\tEnter a metric: ")
#         a.append({'label': label, 'key': key_name, 'metric': metric})
#         exit = raw_input('Do you need to create more keys? (y/n) ')
#         if exit == 'n':
#             return a


def import_keys(script_name):
    with open('scripts/' + script_name + '/schema.json') as schema_file:    
        schema = json.load(schema_file)
    return schema['keys']


def create_rca(auth_token, monitor_data):
    try:
        req = urllib2.Request('https://api.rapidspike.com/v1/rcamonitors')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', 'Bearer ' + auth_token)

        res_raw = urllib2.urlopen(req, json.dumps(monitor_data))
        res_data = json.load(res_raw)

        print "The RCA monitor has been created in your account."
        return res_data
    except urllib2.HTTPError, err:
        print "Something happened! Error code", err.code
    except urllib2.URLError, err:
        print "Some other error happened:", err.reason

    # The API call must have failed, so exit!
    sys.exit()


def store_monitor_uuid(script_name, monitor_uuid):
    file_path = 'scripts/' + script_name + '/config.json'
    with open(file_path + '.template') as config_file:    
        config = json.load(config_file)
    
    config['uuid'] = monitor_uuid
    f = open(file_path, 'w')
    f.write(json.dumps(config))
    f.close()


def install_dependencies(script_name):
    file_path = 'scripts/' + script_name + '/config.json'
    with open(file_path + '.template') as config_file:    
        config = json.load(config_file)

    try:
        requires = config['requires']
        print "\nThe script has dependencies:"
        for requirement in requires:
            print "\t- ", requires[0]
    except KeyError:
        return None

    exit = raw_input("\nPress any key to continue...")
    return True


def run_script(script_name):
    print "\nRunning the script for the first time, please wait..."
    try:
        response = subprocess.check_output(
            ['python', 'scripts/' + script_name + '/run.py'],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        return response
    except subprocess.CalledProcessError:
        return None
    print "The script has been setup and run successfully!"


def add_to_run_list(script_name, monitor_uuid):
    file_path = 'config/run_list.json'
    with open(file_path) as run_list_file:    
        run_list = json.load(run_list_file)

    # for run_item in run_list:
    #     if run_item['script'] == script_name:
    #         exit = raw_input("\nYou have already configured this script, are you sure you wish to continue? (y/n) ")
    #         if exit == 'n':
    #             return False

    freq = raw_input("\nPlease enter the frequency at which you would like the script to be run (minutes): ")
    run_list.append({'script': script_name, 'frequency': freq, 'monitor_uuid': monitor_uuid})
    
    f = open(file_path, 'w')
    f.write(json.dumps(run_list))
    f.close()


# def setup_cron():


print "================================================================="
print "          ____              _     _______       _ __       "
print "         / __ \____ _____  (_)___/ / ___/____  (_) /_____  "
print "        / /_/ / __ `/ __ \/ / __  /\__ \/ __ \/ / //_/ _ \ "
print "       / _, _/ /_/ / /_/ / / /_/ /___/ / /_/ / / ,< /  __/ "
print "      /_/ |_|\__,_/ .___/_/\__,_//____/ .___/_/_/|_|\___/  "
print "                 /_/                 /_/                   "
print "        ___  ________     ____         __       ____       "
print "       / _ \/ ___/ _ |   /  _/__  ___ / /____ _/ / /__ ____"
print "      / , _/ /__/ __ |  _/ // _ \(_-</ __/ _ `/ / / -_) __/"
print "     /_/|_|\___/_/ |_| /___/_//_/___/\__/\_,_/_/_/\__/_/   "
print "================================================================="
print "\nWelcome to the RapidSpike RCA installer!"

auth_token = login()
script_name = request_script()

monitor_data = {
  'monitor':{'label': raw_input("\nWhat would you like to name this RCA monitor? ")},
  'keys': import_keys(script_name)
}

create_output = create_rca(auth_token, monitor_data)

monitor_uuid = create_output['data']['monitor']['uuid']
add_to_run_list(script_name, monitor_uuid)
store_monitor_uuid(script_name, monitor_uuid)
install_dependencies(script_name)

run_script(script_name)
# setup_cron()

print "\nTo view the monitor, visit https://my.rapidspike.com/#/account/rca/" + monitor_uuid
print "Please allow a few minutes for the first result data to be received into the system.\n"

print "================================================================="
print "      ______ __                   __      __  __              "
print "     /_  __// /_   ____ _ ____   / /__    \ \/ /____   __  __ "
print "      / /  / __ \ / __ `// __ \ / //_/     \  // __ \ / / / / "
print "     / /  / / / // /_/ // / / // ,<        / // /_/ // /_/ /  "
print "    /_/  /_/ /_/ \__,_//_/ /_//_/|_|      /_/ \____/ \__,_/   "
print "================================================================="