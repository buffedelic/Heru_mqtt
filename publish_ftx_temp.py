#!/usr/bin/env python3

import minimalmodbus
import sys
from decimal import *
import paho.mqtt.publish as mqtt
import sched, time
from heru import HeruFTX

device = '/dev/ttyUSB0'
port = 1

minimalmodbus._print_out( 'HERU FTX MQTT PUBLISHER')

loopTime = 60

s = sched.scheduler(time.time, time.sleep)
def publish(sc):
	
	print("Instrument started ")
	instr = HeruFTX(device, port)
	instr.mode = minimalmodbus.MODE_RTU
	instr.serial.stopbits = 1
	instr.serial.timeout  = 0.2
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
			i = i - 65536 #65535 ar hogsta mojliga int()
		i = float(i) / 10
		tempDec.append(i)

	mqtt_server = 'homeassistant.lan'
	mqtt_user = 'buff'
	mqtt_password = 'mammas'

	def publish_message(message, topic=""):

		print("Publishing to MQTT message: ")
		print(str(message) )
		mqtt.multiple(message, hostname=mqtt_server, auth={'username':mqtt_user, 'password':mqtt_password}, client_id="Heru temp")

	message = []
	message.append({'topic':"hvac/heru/temp/outside_temp",'payload': "{}".format(str(tempDec[0]))})
	message.append({'topic':"hvac/heru/temp/supply_temp", 'payload': "{}".format(str(tempDec[1]))})
	message.append({'topic':"hvac/heru/temp/exhaust_temp", 'payload': "{}".format(str(tempDec[2]))})
	message.append({'topic':"hvac/heru/temp/waste_temp", 'payload': "{}".format(str(tempDec[3]))})
	message.append({'topic':"hvac/heru/temp/wheel_temp", 'payload': "{}".format(str(tempDec[5]))})


	print("Got these temperatures from hvac:")
	print(tempDec)
	print("---------------------------------------------------")

	publish_message(message)    
	
	s.enter(loopTime, 1, publish, (sc,))

s.enter(loopTime, 1, publish, (s,))
s.run()