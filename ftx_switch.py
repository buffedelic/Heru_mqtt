#!/usr/bin/env python3
# -*- coding: utf-8 -

from heru import HeruFTX
import minimalmodbus
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time



instr = HeruFTX('/dev/ttyUSB0', 1) #port, slaveadress
instr.mode = minimalmodbus.MODE_RTU
instr.serial.timeout  = 0.2 #Timeout might be adjusted to allow full reading of message
instr.debug = False
instr.precalculate_read_size = False

switch = ["hvac/heru/power/set",
         "hvac/heru/over_pressure_mode/set",
         "hvac/heru/boost_mode/set",
         "hvac/heru/away_mode/set",
         "hvac/heru/clear_alarms/set",
         "hvac/heru/clear_filter_alarms/set"] 

def on_subscribe(client, userdata, mid, granted_qos):
    #function to anounce availability
    print("Subscribed: "+str(mid)+" "+str(granted_qos)+" "+str(userdata)+" "+str(client))
    print("Polling register " + str(mid) + " " + switch[ int(mid) - 1 ])
    poll_device(int(mid))

def on_message(client, userdata, msg):
    #handle message
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    print("Setting register " + str(switch.index(msg.topic) + 1) + " " + msg.topic)
    instr.set_coil_status(switch.index(msg.topic) + 1, int(msg.payload))

def poll_device(register):
    answer = None
    while answer is None:
        try:
            answer = instr.get_coil_status(register)
        except:
            pass         
    publish.single(switch[register - 1], answer, qos = 2, retain=True, hostname="homeassistant.lan", auth={'username':"buff", 'password':"mammas"}, client_id="IVT")

    

if __name__ == '__main__':

### Functioncode 5 ########
#0x00001 Unit on
#0x00002 Overpressure mode
#0x00003 Boost mode
#0x00004 Away mode
#0x00005 Clear Alarms
#0x00006 Reset filter timer
###########################
    
    broker_adress='homeassistant'
    subscribe_topic='hvac/heru/power/set'
    print("Connecting to broker {}".format(broker_adress))
    client = mqtt.Client(client_id="Heru control", clean_session=True)
    client.username_pw_set("buff", "mammas")
    client.connect(broker_adress, 1883)
    client.on_subscribe = on_subscribe
    #client.on_connect = on_connect
    client.on_message = on_message

    for topic in switch:
        client.subscribe(topic)
    client.loop_start()
    # client.loop_forever()

    while True:
        # pass
        time.sleep(15)
        for i in range(1, 7):
            print("polling register: " + str(i))
            poll_device(i)
            time.sleep(2)


pass
