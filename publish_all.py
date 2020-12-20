#!/usr/bin/env python3

from instrument import HeruFTX
import minimalmodbus

device = '/dev/ttyUSB0'
port = 1

minimalmodbus._print_out( 'HERU FTX MQTT PUBLISHER')

instrument = HeruFTX(device, port)
instrument.mode = minimalmodbus.MODE_RTU
instrument.serial.stopbits = 1
instrument.serial.timeout  = 0.2
instrument.debug = False
instrument.precalculate_read_size = False

print(instrument.coil_status(human=True))
print(instrument.coil_status(human=False))