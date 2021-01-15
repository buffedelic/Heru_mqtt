#!/usr/bin/env python3
# -*- coding: utf-8 -

import minimalmodbus
from heru import HeruFTX
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
from safe_schedule import SafeScheduler
import sys
from decimal import *

#########################################-SETTINGS-###########################################################
# Minimalmodbus constants
device_port = '/dev/ttyUSB0'
device_id = 1

# MQTT constants
mqtt_broker =       'homeassistant'
mqtt_user =         'buff'
mqtt_password =     'mammas'
switch_topic = [    "hvac/heru/power/set",                  # Index citical! Both subscribe and publish topics
                    "hvac/heru/over_pressure_mode/set",
                    "hvac/heru/boost_mode/set",
                    "hvac/heru/away_mode/set",
                    "hvac/heru/clear_alarms/set",
                    "hvac/heru/clear_filter_alarms/set"]

# Function booleans
heru_feedback   = True      # Enables feedback or polling if remotecontrol har changes settings, problematic... Requirest heru_control = True
heru_control    = True      # Enable control via mqtt
heru_temp       = True      # Reporting temperatures via mgtt

# Scheduler times, minutes
t_temp = 1
t_switch = 5   # Polling to ofter seems to break instr connection and throwing exception in scheduler thread, therefore safescheduler
t_alarm = 120

####################################################################################################

def fetch_temp():
    message = []
    temp = None
    while temp is None:
        try:
            temp = instr.read_registers(1, 7, functioncode=4)
        except:
            print("Failed to read temperaures from instrument")

    tempDec = []
    for i in temp:
        if i > 6000:
            i = i - 65536 #65535 ar hogsta mojliga int()
        i = float(i) / 10
        tempDec.append(i)

    message.append({'topic':"hvac/heru/temp/outside_temp",'payload': "{}".format(str(tempDec[0]))})
    message.append({'topic':"hvac/heru/temp/supply_temp", 'payload': "{}".format(str(tempDec[1]))})
    message.append({'topic':"hvac/heru/temp/exhaust_temp", 'payload': "{}".format(str(tempDec[2]))})
    message.append({'topic':"hvac/heru/temp/waste_temp", 'payload': "{}".format(str(tempDec[3]))})
    message.append({'topic':"hvac/heru/temp/wheel_temp", 'payload': "{}".format(str(tempDec[5]))})

    return message

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for topic in switch_topic:
        client.subscribe(topic)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos)+" "+str(userdata)+" "+str(client))
    poll_device(int(mid)) # Update real world setting as basepiont

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    #print("Setting register " + str(switch.index(msg.topic) + 1) + " " + msg.topic)
    instr.set_coil_status(switch_topic.index(msg.topic) + 1, int(msg.payload))

def poll_device(register):
    answer = instr.get_coil_status(register)
    if answer is not None:
        publish.single(switch_topic[register - 1], answer, qos = 2, retain=True, hostname="homeassistant.lan", auth={'username':"buff", 'password':"mammas"}, client_id="Heru Control")

def update_switches():
    for i in range(1, 5):
        poll_device(i)
        time.sleep(2)

def update_alarms():
    for i in range(5, 7):
        poll_device(i)
        time.sleep(2)

def publish_temp():
    print("Publishing temperatures to MQTT: ")
    message = fetch_temp()
#    print(str(message) )
    publish.multiple(message, hostname=mqtt_broker, auth={'username':mqtt_user, 'password':mqtt_password}, client_id="Heru temp")

if __name__ == '__main__':
    '''
    Initiating rs-485 bus
    '''
    minimalmodbus._print_out( 'HERU FTX MQTT PUBLISHER')
    instr = HeruFTX(device_port, device_id)
    instr.mode = minimalmodbus.MODE_RTU
    instr.serial.stopbits = 1
    instr.serial.timeout  = 0.2
    instr.debug = False
    instr.precalculate_read_size = False
    print("Instrument started ")

    schedule = SafeScheduler()

    if heru_temp: 
        print("Temperature enabled")
        schedule.every(t_temp).minutes.do(publish_temp)
    if heru_control: 
        print("Control enabled")
        # print("Connecting to broker {}".format(broker_adress))
        client = mqtt.Client(client_id="Heru control", clean_session=True)
        client.username_pw_set(mqtt_user, mqtt_password)
        client.connect(mqtt_broker, 1883)
        client.on_subscribe = on_subscribe
        client.on_message = on_message
        client.on_connect = on_connect
        client.loop_start()
    if heru_feedback and heru_control:
        print("Control with feedback enabled")
        schedule.every(t_switch).minutes.do(update_switches)
        schedule.every(t_alarm).minutes.do(update_alarms)

    while True:
        schedule.run_pending()
        time.sleep(1)

pass
