#!/usr/bin/env python3
# -*- coding: utf-8 -

from heru import HeruFTX
import minimalmodbus
import paho.mqtt.client as mqtt

instr = HeruFTX('/dev/ttyUSB0', 1) #port, slaveadress
instr.mode = minimalmodbus.MODE_RTU
instr.serial.timeout  = 0.2 #Timeout might be adjusted to allow full reading of message
instr.debug = False
instr.precalculate_read_size = False


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

	instr.set_coil_status(3, "on")

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
