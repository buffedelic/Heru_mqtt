#!/usr/bin/env python3
# -*- coding: utf-8 -

from heru.heru import HeruFTX
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
from safe_schedule import SafeScheduler
import json
import os

# ##########################-SETTINGS-##########################
debug = False  # Set to True to troubleshoot connection to broker, syslog

# Minimalmodbus constants
device_port = '/dev/ttyUSB0'
device_id = 1

# MQTT constants
mqtt_broker = '192.168.1.219'
mqtt_broker_port = 1883
mqtt_user = 'buff'
mqtt_password = 'mammas'
switch_topic = [
    "hvac/heru/power/set",  # Index citical! Both subscribe and publish topics
    "hvac/heru/over_pressure_mode/set",
    "hvac/heru/boost_mode/set",
    "hvac/heru/away_mode/set",
    "hvac/heru/clear_alarms/set",
    "hvac/heru/clear_filter_alarms/set"
]
sensor_topic = [  # Index critical, hardwired in temperature resonse
    "hvac/heru/temp/outside_temp",
    "hvac/heru/temp/supply_temp",
    "hvac/heru/temp/exhaust_temp",
    "hvac/heru/temp/waste_temp",
    "hvac/heru/temp/water_temp",  # not used
    "hvac/heru/temp/wheel_temp",
    "hvac/heru/temp/room_temp"  # not used
]
exchange_efficiency_topic = [
    "hvac/heru/efficiency/temperature_efficiency",
    "hvac/heru/efficiency/energy_exchange"
]

# Function booleans
heru_feedback = True  # Enables polling if remotecontrol has changed settings
heru_control = True   # Enable control via mqtt
heru_temp = True      # Reporting temperatures via mgtt

# Scheduler times, minutes
t_temp = 1
t_switch = 5
t_alarm = 120

# ##########################-HERU FUNCTIONS-##########################


def fetch_temp():

    # Response is a plain list without description
    # 0 Outdoor temperature                     3.3°C
    # 1 Supply air temperature                  17.2°C
    # 2 Exhaust air temperature                 19.7°C
    # 3 Waste air temperature                   3.3°C
    # 4 Water temperature                       58.9°C
    # 5 Heat Recovery Wheel temperature         15.5°C
    # 6 Room temperature                        59.0°C

    message = []
    fetch_retry_succeded = False
    tempList = None
    while tempList is None:
        try:
            tempList = heru.read_registers(1, 7, functioncode=4)
        except:
            print("Failed to read temperaures from instrument, retrying...")
            fetch_retry_succeded = True
    if fetch_retry_succeded:
        print("Successfull fetch from device after retry")

    index = 0
    for temp in tempList:
        message.append({
            'topic': sensor_topic[index],
            'payload': "{}".format(str(format_temperature(temp)))})
        index += 1

    """ Heat exchanger calculation
    n=(ti-tu)/(tf-tu)

    ti = tilluft temperatur (efter växlaren/till rummen)
    tu = uteluft temperatur
    tf = frånluft temperatur (från rummen)
    q = luftflöde m3/h, balanserat system

    kW = ((q/3600)*1.2*(ti - tu) * 100)/100

    Required energy to heat up incoming air
    P = Q x 1,296 x Δt
    
    P = effekt i W (effekten på värmebatteriet som vi ska räkna ut)
    Q = luftflöde i l/s (det luftflödet du räknat ut tidigare enligt ovan formel)
    Δt = temperaturhöjning i °C
    """
    
    temp_efficiency = (
        100 * ((format_temperature(tempList[1]) - format_temperature(tempList[0])) / (format_temperature(tempList[2]) - format_temperature(tempList[0])))
    )
    message.append({
        'topic': exchange_efficiency_topic[0],
        'payload': "{}".format(str(round(float(temp_efficiency), 2)))})

    energy_efficiency = (
        ((260 / 3600) * 1.2 * (format_temperature(tempList[1]) - format_temperature(tempList[0])) * 100)/100
    )
    if debug:
        print(tempList[1])
        print(tempList[0])
        print(tempList[1] - tempList[0])
        print(energy_efficiency)

    if energy_efficiency < 0:
        energy_efficiency = 0

    message.append({
        'topic': exchange_efficiency_topic[1],
        'payload': "{}".format(str(round(float(energy_efficiency), 2)))})

    return message


def format_temperature(temp):
    if temp > 6000:
        temp = temp - 65536  # 65535 är högsta möjliga int(), negativt
    temp = float(temp) / 10
    return temp


def poll_device(register):
    answer = heru.get_coil_status(register)
    if answer is not None:
        publish.single(
            switch_topic[register - 1],
            answer,
            qos=2,
            retain=True,
            hostname=mqtt_broker,
            auth={'username': mqtt_user, 'password': mqtt_password},
            client_id="HeruControl-Poll")


def update_switches():
    for i in range(1, 5):
        poll_device(i)
        time.sleep(2)


def update_alarms():
    for i in range(5, 7):
        poll_device(i)
        time.sleep(2)


# ##########################-MQTT FUNCTIONS-##########################


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    sensor_config = []
    for i in range(len(sensor_topic)):
        sensor = sensor_topic[i].split('/')[3]
        sensor_config.append({
            'topic': "homeassistant/sensor/heru/heru-{0}/config".format(sensor),
            'payload': json.dumps({
                'name': "Heru {}".format(sensor.replace('_', ' ').capitalize()),
                'state_topic': "{}".format(sensor_topic[i]),
                'unique_id': "heru_{}".format(sensor),
                'device_class': "temperature",
                'unit_of_meas': "°C",
                'device': {
                    'name': "Heru",
                    'model': "100s EC A",
                    'manufacturer': "Östberg",
                    "identifiers": ["HERU1"]}
            }, indent=2, ensure_ascii=False),
            'qos': 2,
            'retain': True})

    switch_config = []
    for i in range(len(switch_topic)):
        switch = switch_topic[i].split('/')[2]
        switch_config.append({
            'topic': "homeassistant/switch/heru/heru-{0}/config".format(switch),
            'payload': json.dumps({
                'command_topic': "hvac/heru/{}/set".format(switch),
                'name': "Heru {}".format(switch.replace('_', ' ').capitalize()),
                'state_topic': "{}".format(switch_topic[i]),
                'unique_id': "heru_{}".format(switch),
                'payload_on': "1",
                'payload_off': "0",
                'state_off': "0",
                'state_on': "1",
                'device': {
                    'name': "Heru",
                    'model': "100s EC A",
                    'manufacturer': "Östberg",
                    "identifiers": ["HERU1"]}
            }, indent=2, ensure_ascii=False),
            'qos': 2,
            'retain': True})

    exchange_efficiency = []
    for i in range(len(exchange_efficiency_topic)):
        sensor = exchange_efficiency_topic[i].split('/')[3]
        if i == 1:
            unit = "kW"
        else:
            unit = "%"
        sensor_config.append({
            'topic': "homeassistant/sensor/heru/heru-{0}/config".format(sensor),
            'payload': json.dumps({
                'name': "Heru {}".format(sensor.replace('_', ' ').capitalize()),
                'state_topic': "{}".format(exchange_efficiency_topic[i]),
                'unique_id': "heru_{}".format(sensor),
                'device_class': "power_factor",
                'unit_of_meas': unit,
                'device': {
                    'name': "Heru",
                    'model': "100s EC A",
                    'manufacturer': "Östberg",
                    "identifiers": ["HERU1"]}
            }, indent=2, ensure_ascii=False),
            'qos': 2,
            'retain': True})

    config = sensor_config + switch_config + exchange_efficiency
    publish.multiple(
        config,
        hostname=mqtt_broker,
        auth={'username': mqtt_user, 'password': mqtt_password},
        client_id="HeruConfig")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for topic in switch_topic:
        client.subscribe(topic)


def on_subscribe(client, userdata, mid, granted_qos):
    if debug:
        print(
            "Subscribed: " +
            str(mid) + " " +
            str(granted_qos) + " " +
            str(userdata) + " " +
            str(client))
    poll_device(int(mid))  # Update real world setting as basepiont


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    heru.set_coil_status(switch_topic.index(msg.topic) + 1, int(msg.payload))


def publish_temp():
    print("Publishing temperatures to MQTT broker")
    message = fetch_temp()
    publish.multiple(
        message,
        hostname=mqtt_broker,
        auth={'username': mqtt_user, 'password': mqtt_password},
        client_id="HeruTemp")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
        while not check_ping():
            print("Trying to reconnect in 5 seconds")
            time.sleep(5)
        # client.reconnect()


def on_log(client, obj, level, string):
    if debug:
        print(string)


def check_ping():
    hostname = "192.168.1.1"
    response = os.system("ping -c 1 " + hostname)
    # and then check the response...
    if response == 0:
        local_conn = True
    else:
        local_conn = False

    return local_conn


# def restart():
#     command = "/usr/bin/sudo /sbin/shutdown -r now"
#     import subprocess
#     process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
#     output = process.communicate()[0]
#     print output

def connect_mqtt():
    client = mqtt.Client(client_id="HeruControl", clean_session=True)
    client.username_pw_set(mqtt_user, mqtt_password)
    client.connect(mqtt_broker, mqtt_broker_port)
    client.on_log = on_log
    client.reconnect_delay_set(min_delay=1, max_delay=120)
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.loop_start()


if __name__ == '__main__':
    '''
    Initiating rs-485 bus
    '''
    print("-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-")
    print("-#  HERU FTX MQTT PUBLISHER STARTED  #-")
    print("-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-")
    heru = HeruFTX(device_port, device_id)
    print("Instrument initialized and started")

    schedule = SafeScheduler()

    if heru_temp:
        print("Temperature reporting enabled")
        schedule.every(t_temp).minutes.do(publish_temp)
    if heru_control:
        print("Control functions enabled")
        connect_mqtt()
        if heru_feedback:
            print("Control functions with polling of remote enabled")
            schedule.every(t_switch).minutes.do(update_switches)
            schedule.every(t_alarm).minutes.do(update_alarms)
            # schedule.every(60).minutes.do(connect_mqtt)
    print("-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-")

    while True:
        schedule.run_pending()
        time.sleep(1)

pass
