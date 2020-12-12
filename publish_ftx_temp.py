#!/usr/bin/env python3

import minimalmodbus
import sys
from decimal import *
import paho.mqtt.publish as mqtt

ior = 0

instr = minimalmodbus.Instrument('/dev/ttyUSB0', 1) #port, slaveadress
instr.debug = False
instr.precalculate_read_size = False

temp = None
while temp is None:
	try:
		temp = instr.read_registers(1, 7, functioncode=4)
	except:
		pass

tempDec = []
for i in temp:
	if i > 6000:
		ior = i
		i = i - 65536 #65535 ar hogsta mojliga int()
	i = float(i) / 10
	tempDec.append(i)

mqtt_server = 'homeassistant.lan'
mqtt_user = 'buff'
mqtt_password = 'mammas'

def publish_message(message, topic=""):


	print("Publishing to MQTT topic: " + topic)
	print("Message: " + str(message) )
	mqtt.multiple(message, hostname=mqtt_server, auth={'username':mqtt_user, 'password':mqtt_password}, client_id="Heru temp")

message = []
#[{'topic': '<topic>', 'payload': '<payload>'}, {'topic': '<topic>', 'payload': '<payloads>'}]
message.append({'topic':"hvac/heru/outside_temp",'payload': "{}".format(str(tempDec[0]))})
message.append({'topic':"hvac/heru/supply_temp", 'payload': "{}".format(str(tempDec[1]))})
message.append({'topic':"hvac/heru/exhaust_temp", 'payload': "{}".format(str(tempDec[2]))})
message.append({'topic':"hvac/heru/waste_temp", 'payload': "{}".format(str(tempDec[3]))})
message.append({'topic':"hvac/heru/wheel_temp", 'payload': "{}".format(str(tempDec[5]))})


print("Got these values from hvac:")
print(tempDec)
print("---------------------------------------------------")
publish_message(message)
#[3.7, 18.5, 20.4, 8.9, 58.9, 17.2, 59.0]
