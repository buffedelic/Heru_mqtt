#!/usr/bin/env python3
# -*- coding: utf-8 -

import instrument
import paho.mqtt.client as mqtt

instr = HeruFTX('/dev/ttyUSB0', 1) #port, slaveadress
instr.mode = minimalmodbus.MODE_RTU
instr.serial.timeout  = 0.2 #Timeout might be adjusted to allow full reading of message
instr.debug = False
instr.precalculate_read_size = False



#instr = minimalmodbus.Instrument('/dev/ttyUSB0', 1) #port, slaveadress
#instr.precalculate_read_size = False
#instr.debug = True

#switch = ["Unit on", "Overpressure mode", "Boost mode", "Away mode", "Clear alarms",
#          "Reset filter timer"]
statusstr = ["off", "on"]

def set_switch(register, state):
	# will put FTX in desired state if not allready.

	if state == "on":
		if read_status(register) == 0:
			switch_status(0, register)
		else:
			print("No change in state")
			pass
	elif state == "off":
		if read_status(register) == 1:
			switch_status(1, register)
		else:
			print("No change in state")
			pass

def read_status(register):
	status = None
	while status is None:
		try:
			status = instr.read_bit(register, functioncode=1) #Read state
			print("{} is {}".format(switch[register], statusstr[status]))
			return status
		except:
			pass

def switch_status(status, register):
	if status == 1:
		switched_status = 0
	else:
		switched_status = 1
	done = False
	while not done:
		try:
			instr.write_bit(register, switched_status, functioncode=5) #Switch between on/off
			done = True
			print("{} switched to {}".format(switch[register], statusstr[switched_status]))
		except:
			pass

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload)) 


if __name__ == '__main__':

### Functioncode 5 ########
#0x00001 Unit on
#0x00002 Overpressure mode
#0x00003 Boost mode
#0x00004 Away mode
#0x00005 Clear Alarms
#0x00006 Reset filter timer
###########################

#	set_switch(2,"off")
#	set_switch(3, "off")

	broker_adress='homeassistant.lan'
	subscribe_topic='hvac/heru/power/set'

	print("Connecting to broker {}".format(broker_adress))
	client = mqtt.Client("Heru Client")
#	client.username_pw_set("buff", "mammas")
	client.on_subscribe = on_subscribe
#	client.on_connect = on_connect
	client.connect(broker_adress, 1883)
	print(client.subscribe("hvac/heru/mode/set"))
	client.loop_forever()
#	print(client.subscribe(subscribe_topic))
#	client.publish("hvac/heru/power/set","on")

pass
