#!/usr/bin/env python3

import sys
import logging
import threading
from configparser import ConfigParser
import os.path
import argparse
from inkbird_pool_sensor import InkBirdPoolSensor

from flask import Flask, abort

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
        
# Argparse

project_name = 'Inkbird REST API provider for Bluetooth pool sensor'
project_url = 'https://github.com/garethnz/Inkbird-IBS-P01B-REST'

parser = argparse.ArgumentParser(description=project_name, epilog='For further details see: ' + project_url)
parser.add_argument('--config_dir', help='set directory where config.ini is located', default=sys.path[0])
parser.add_argument('--nodaemon', help='For one time execution (no daemon mode) set to True', default=False)
parse_args = parser.parse_args()

# Load configuration file
config_dir = parse_args.config_dir
nodaemon_arg = parse_args.nodaemon

config = ConfigParser(delimiters=('=', ), inline_comment_prefixes=('#'))
config.optionxform = str
try:
    with open(os.path.join(config_dir, 'config.ini')) as config_file:
        config.read_file(config_file)
except IOError:
    logging.error('No configuration file "config.ini"')
    sys.exit(1)

peripheral_mac = config['Sensors'].get('PoolSensor', 'PoolSensor')
read_interval = int(config['Daemon'].get('read_interval', 3600))
run_as_daemon = config['Daemon'].get('enabled', True)

#Prep inkbird
inkbird_poolsensor = InkBirdPoolSensor(peripheral_mac)
#

if nodaemon_arg or not run_as_daemon:
    logging.info("non daemon mode")
    
    inkbird_poolsensor.read_current_value()
    
    exit()
else:    
    daemon_thread = threading.Thread(target=inkbird_poolsensor.daemon_function_loop, args=(read_interval,), daemon=True)
    daemon_thread.start()

# Start rest-api
app = Flask(__name__)
@app.route("/temperature")
def main():
    global inkbird_poolsensor
    
    if inkbird_poolsensor.current_temp is False:
        return abort(404)
    else:
        return str(f"{inkbird_poolsensor.current_temp}")
app.run(host="0.0.0.0")