#!/usr/bin/env python3

import ssl
import sys
from time import sleep
import simplepyble
#import paho.mqtt.client as mqtt
import logging
from configparser import ConfigParser
import os.path
import argparse

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.DEBUG,
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

#topic = config['MQTT'].get('topic', "/test/sensor/pool") 
peripheral_mac = config['Sensors'].get('PoolSensor', 'PoolSensor')
read_interval = int(config['Daemon'].get('read_interval', 3600))
run_as_daemon = config['Daemon'].get('enabled', True)

if nodaemon_arg:
    run_as_daemon = False
    logging.info("non daemon mode")

def float_value(nums):
    # check if temp is negative
    num = (nums[1]<<8)|nums[0]
    if nums[1] == 0xff:
        num = -( (num ^ 0xffff ) + 1)
    return float(num) / 100

def c_to_f(temperature_c):
    return 9.0/5.0 * temperature_c + 32

def connect_to_peripheral():
    adapters = simplepyble.Adapter.get_adapters()

    if len(adapters) == 0:
        print("No adapters found")

    adapter = adapters[0]
    result = adapter.scan_for(5000)
    peripherals = adapter.scan_get_results()

    for i, peripheral in enumerate(peripherals):
        if peripheral.address() == peripheral_mac:
            return peripheral
    return None

peripheral = connect_to_peripheral()
if peripheral is None:
    print(f"Peripheral {peripheral_mac} not found")
    exit()
print(f"Connecting to {peripheral_mac}")

# TODO: ensure disconnect
peripheral.connect()

def get_temperature_service(peripheral):
    # TODO add these to config.ini
    characteristic_uuid = "0000fff2-0000-1000-8000-00805f9b34fb"
    services = peripheral.services()
    print(f"Looking for service and characteristic")
    for service in services:
        for characteristic in service.characteristics():
            print(f"{service.uuid()} {characteristic.uuid()}")
            if characteristic.uuid() == characteristic_uuid:
                return service, characteristic
    return None, None

service, characteristic = get_temperature_service(peripheral)

if service is None or characteristic is None:
    logging.error("Unable to find required service or characteristic")
    exit()

def read_current_value():
    try:
        return peripheral.read(service.uuid(), characteristic.uuid())
    except Exception as e:
        logging.error("Error reading BTLE: {}".format(e))
        return False

# TODO: New thread
    # app.run()
while True:
    current_value = read_current_value()
    if not current_value:
        continue

    logging.debug("raw data: {}".format(current_value))

    # little endian, first two bytes are temp
    temperature_c = float_value(current_value[0:2])
    logging.info("temperature: {}".format(temperature_c))

    #result = mqtt_client.publish('{}/celsius'.format(topic),temperature_c)

    # if result[0] == 0:
    #     logging.debug("mqtt: sent {}, {}".format(topic,temperature_c))
    # else:
    #     logging.info("mqtt: failed to send {}".format(topic))

    if run_as_daemon:
        logging.debug('Going to sleep for {} seconds ...'.format(read_interval))
        sleep(read_interval)
    else:
        logging.info('One time execution done, exiting')
        #mqtt_client.disconnect()
        break

peripheral.disconnect()