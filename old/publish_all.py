#!/usr/bin/env python3

from heru import HeruFTX
import minimalmodbus
import paho.mqtt.publish as mqtt
import schedule

l_poll_minutes = 1 #Update frequenzy, minutes

device = '/dev/ttyUSB0'
port = 1
qtt_server = 'homeassistant.lan'
mqtt_user = 'buff'
mqtt_password = 'mammas'

coil_status_text = ['Unit on','Overpressure mode','Boost mode','Away mode','Clear Alarms','Reset filter timer',]
input_status_text = ['Fire alarm switch','Boost switch','Overpressure switch','Aux switch','Fire alarm','Rotor alarm','RFU','Freeze alarm','Low supply alarm','Low rotor temperature alarm','RFU','RFU','Temp. sensor open circuit alarm','Temp. sensor short circuit alarm','Pulser alarm','Supply fan alarm','Exhaust fan alarm','Supply filter alarm','Exhaust filter alarm','Filter timer alarm','Freeze protection B level','Freeze protection A level','Startup 1st phase','Startup 2nd phase','Heating','Recovering heat/cold','Cooling','CO2 boost','RH boost']
input_register_text = ['Component ID','Outdoor temperature','Supply air temperature','Exhaust air temperature','Waste air temperature','Water temperature','Heat Recovery Wheel temperature','Room temperature','RFU','RFU','RFU','Supply pressure','Exhaust pressure','Relative humidity','Carbon dioxide','RFU','RFU','Sensors open','Sensors shorted','Filter days left','Current weektimer program','Current fan speed','Current supply fan step','Current exhaust fan step','Current supply fan power','Current exhaust fan power','Current supply fan speed','Current exhaust fan speed','Current heating power','Current heat/cold recovery power','Current cooling power','Supply fan control voltage','Exhaust fan control voltage',]
holding_register_text = ['User fan speed','Temperature setpoint','Supply fan speed, EC','Exhaust fan speed, EC','Min exhaust fan speed, EC','Mod exhaust fan speed, EC','Max exhaust fan speed, EC','RFU','RFU','Min supply temperature','Max supply temperature','Regulation mode','SNC indoor-outdoor diff. Limit','SNC exhaust low limit','SNC exhaust high limit','SNC enable','Freeze protection limit temperature','RFU','RFU','CO2 limit','CO2 interval','CO2 ramp','RH limit','RH interval','RH ramp','Boost speed','Boost duration','Overpressure duration','Supply cold limit A','Supply cold limit B','Fire sensor type','RFU','Supply pressure sensor type','Exhaust pressure sensor type','Supply pressure switch present','Exhaust pressure switch present','Filter measurement, weekday','Filter measurement, hour','Filter measurement, minute','Filter speed increase','RFU','RFU','RFU','Filter change period','Alarm relay option 1','Alarm relay option 2','RFU','RFU','RFU','Water heater connected','Electric heater connected','Cooler connected','Flow direction','RFU','RFU','RFU','RFU','RFU','RFU','Clock, Weekday','Clock, Hours','Clock, Minutes','Clock, Seconds','RFU','RFU','RFU','RFU','RFU','Weektimer enable','WT1 on hour','WT1 on minute','WT1 off hour','WT1 off minute','WT1 weekdays','WT1 temperature setpoint','WT1 fan speed','RFU','RFU','RFU','WT2 on hour','WT2 on minute','WT2 off hour','WT2 off minute','WT2 weekdays','WT2 temperature setpoint','WT2 fan speed','RFU','RFU','RFU','WT3 on hour','WT3 on minute','WT3 off hour','WT3 off minute','WT3 weekdays','WT3 temperature setpoint','WT3 fan speed','RFU','RFU','RFU','WT4 on hour','WT4 on minute','WT4 off hour','WT4 off minute','WT4 weekdays','WT4 temperature setpoint','WT4 fan speed','RFU','RFU','RFU','WT5 on hour','WT5 on minute','WT5 off hour','WT5 off minute','WT5 weekdays','WT5 temperature setpoint','WT5 fan speed','Fan type','EC fan max speed','Rotor pulsing period']

def publish_message(message, topic=""):

	print("Publishing to MQTT topic: " + topic)
	print("Message: " + str(message) )
	mqtt.multiple(message, hostname=mqtt_server, auth={'username':mqtt_user, 'password':mqtt_password}, client_id="Heru temp")

def handle_time_event():
    
    minimalmodbus._print_out( 'HERU FTX MQTT PUBLISHER')
    instr = HeruFTX(device, port)
    instr.mode = minimalmodbus.MODE_RTU
    instr.serial.stopbits = 1
    instr.serial.timeout  = 0.2
    instr.debug = False
    instr.precalculate_read_size = False

    coil_status = instr.dump_coil_status()
    input_status = instr.dump_input_status()
    input_register = instr.dump_input_register()
    holding_register = instr.dump_holding_register()

    #       Message formatting
    #/----static----/---i_text----/-i_v-
    #/hvac/heru/data/register_name/value

    message = []
    for i in range(len(coil_status)):
        message.append({'topic':"/hvac/heru/data/" + "{}".format(str(coil_status_text[i]).replace(' ','_')), 
                        'payload': "{}".format(str(coil_status[i])),
                        'qos':2})

    for i in range(len(input_status)):
        message.append({'topic':"/hvac/heru/data/" + "{}".format(str(input_status_text[i]).replace(' ','_')), 
                        'payload': "{}".format(str(input_status[i])),
                        'qos':2})

    for i in range(len(input_register)):
        message.append({'topic':"/hvac/heru/data/" + "{}".format(str(input_register_text[i]).replace(' ','_')), 
                        'payload': "{}".format(str(input_register[i])),
                        'qos':2})

    for i in range(len(holding_register)):
        message.append({'topic':"/hvac/heru/data/" + "{}".format(str(holding_register_text[i]).replace(' ','_')), 
                        'payload': "{}".format(str(holding_register[i])),
                        'qos':2})

    print(message)

def main():

    handle_time_event()
    schedule.every(l_poll_minutes).minutes.do(handle_time_event)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()