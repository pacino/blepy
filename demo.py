#!/usr/bin/env python2.7

"""
Example using the generated ble api

Run as e.g. ``python demo.py /dev/ttyUSB0 scan`` to scan for other BLE
devices, or ``python demo.py /dev/ttyUSB0 advertise`` to start
advertising device presence.

Depending on your OS, the format of the port argument will change

Examples
- Windows: COM3
- Mac: /dev/cu.usbmodem1
- Linux: /dev/ttyUSB0
- Raspberry Pi: /dev/ttyACM0


Copyright (c) 2012 Peter Morton
See the file LICENSE for copying permission.

"""

import time
import logging
import sys

import ble  # This is the autogenerated api


# When the ble api reads a message, it calls the appropriate handler
# To override a handler, copy the function definition from ble.py to
# here, then add your own code. Finally, modify the ble module attribute

def evt_connection_disconnected(connection, reason):
    logging.info('connection disconneted, reason={0}'.format(reason))
    ble.cmd_gap_set_mode(ble.GENERAL_DISCOVERABLE, ble.UNDIRECTED_CONNECTABLE)

def rsp_gap_set_mode(result):
    print('GAP mode is set, result={0}'.format(result))

def rsp_system_get_info(build, hw, ll_version, major, minor, patch, protocol_version):
    print('System info: ' + ' '.join(map(str, [build, hw, ll_version, major, minor, patch, protocol_version])))
    
def evt_connection_status(connection, flags, address, address_type, conn_interval, timeout, latency, bonding):
    print('Connected to: ' + ' '.join(address_string(address)))
    
def evt_gap_scan_response(rssi, packet_type, sender, address_type, bond, data):
    address = address_string(sender)
    name = data_string(data)
    print('Scan response {0}: {1}, rssi={2}'.format(address, name, rssi))
    
    
# Override the default methods
ble.evt_connection_disconnected = evt_connection_disconnected
ble.rsp_gap_set_mode = rsp_gap_set_mode    
ble.rsp_system_get_info = rsp_system_get_info
ble.evt_connection_status = evt_connection_status
ble.evt_gap_scan_response = evt_gap_scan_response


# Printing helpers
def address_string(address):
    return ':'.join(['{0:02X}'.format(int(d)) for d in address])

def data_string(data):
    return ''.join(map(chr, data))
    
if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('port')
    parser.add_argument('mode', choices=['scan', 'advertise'])
    parser.add_argument('-l', '--loglevel', default='error')
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()

    # Set up logging
    log_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError('Invalid log level: {0}'.format(loglevel))
    logging.basicConfig(level=log_level, stream=sys.stdout)

    if args.reset:
        ble.init_connect(args.port)
    else:
        ble.connect(args.port)
    ble.cmd_system_get_info()
    ble.read_message(1000)


    if args.mode == 'advertise':
        ble.cmd_gap_set_mode(ble.GENERAL_DISCOVERABLE, ble.UNDIRECTED_CONNECTABLE)
        ble.read_message(1000)
                
    elif args.mode == 'scan':
        ble.cmd_gap_discover(ble.DISCOVER_OBSERVATION)
        ble.read_message(1000)

    # Just run and loop now
    while True:
        try:
            ble.read_message(1000)
        except RuntimeError as err:
            pass
        except KeyboardInterrupt:
            print('disconnecting')
            ble.disconnect()
            break
        


