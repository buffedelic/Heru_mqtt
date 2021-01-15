#!/usr/bin/env python3
# -*- coding: utf-8 -
import sys
sys.path.append('..')
from heru.heru import HeruFTX

# print(minimalmodbus._get_diagnostic_string())

# minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True

if __name__ == '__main__':

    print('HERU FTX MODBUS REGISTER')

    heru = HeruFTX('/dev/ttyUSB0', 1)  # port, slaveadress

    print("---------------")
    print("| Coil Status |")
    print("---------------")
    print('{:40}{:20}{}'.format('Register name', 'Value', 'Description\n'))
    data = heru.dump_coil_status()
    description = ['  ','  ','  ','  ','Write 1 to clear alarm, reads always 0','Write 1 to reset filter timer, reads always 0',]
    text = ['Unit on','Overpressure mode','Boost mode','Away mode','Clear Alarms','Reset filter timer',]

    for line in zip(text, data, description):
        print('{:40}{:20}{}'.format(*line))

    print("----------------")
    print("| Input Status |")
    print("----------------")
    print('{:40}{:20}{}'.format('Register name', 'Value', 'Description\n'))
    data = heru.dump_input_status()
    description = ['  ','  ','  ','  ','  ','  ','Readable, value has no meaning','  ','  ','  ','Readable, value has no meaning','Readable, value has no meaning','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','Supply fan stopped.','No heating or cooling allowed.','  ','  ','  ','  ','  ',]
    text = ['Fire alarm switch','Boost switch','Overpressure switch','Aux switch','Fire alarm','Rotor alarm','RFU','Freeze alarm','Low supply alarm','Low rotor temperature alarm','RFU','RFU','Temp. sensor open circuit alarm','Temp. sensor short circuit alarm','Pulser alarm','Supply fan alarm','Exhaust fan alarm','Supply filter alarm','Exhaust filter alarm','Filter timer alarm','Freeze protection B level','Freeze protection A level','Startup 1st phase','Startup 2nd phase','Heating','Recovering heat/cold','Cooling','CO2 boost','RH boost']

    # for i in text:
    #     print('{0}\t{1}'.format(i,l[text.index(i)]))

    # for c1, c2 in zip(text, l):
    #     print "%-50s %s" % (c1, c2)

    for line in zip(text, data, description):
        print('{:40}{:20}{}'.format(*line))

    print("------------------")
    print("| Input Register |")
    print("------------------")

    print('{:40}{:20}{}'.format('Register name', 'Value', 'Description\n'))
    data = heru.dump_input_register()
    description = ['Always 10','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','Number of days to filter change.','0 = none, 1-5 = program 1-5','0 = Off, 1 = Min, 2 = Std, 3 = Mod, 4 = Max.','0 = Off, 1 = Min, 2 = Std, 3 = Mod, 4 = Max','0 = Off, 1 = Min, 2 = Std, 3 = Mod, 4 = Max','  ','  ','  ','  ','In range 0-255','In range 0-255','In range 0-255','  ','  ']
    unit = ['  ','°C','°C','°C','°C','°C','°C','°C','  ','  ','  ',' Pa',' Pa',' RH',' CO2','  ','  ','  ','  ',' days','  ','  ','  ','  ','%','%',' rpm',' rpm','  ','  ','  ',' x 0.1V',' x 0.1V']
    text = ['Component ID','Outdoor temperature','Supply air temperature','Exhaust air temperature','Waste air temperature','Water temperature','Heat Recovery Wheel temperature','Room temperature','RFU','RFU','RFU','Supply pressure','Exhaust pressure','Relative humidity','Carbon dioxide','RFU','RFU','Sensors open','Sensors shorted','Filter days left','Current weektimer program','Current fan speed','Current supply fan step','Current exhaust fan step','Current supply fan power','Current exhaust fan power','Current supply fan speed','Current exhaust fan speed','Current heating power','Current heat/cold recovery power','Current cooling power','Supply fan control voltage','Exhaust fan control voltage',]
    for line in zip(text, data, unit, description):
        if (line[2] == '°C') or (line[2] == ' Pa'):
            line =list(line)
            line[1] = float(line[1]) / 10
        print('{:40}{}{:20}{}'.format(*line))

    print("----------------------------------------------------")
    print("| Holding Register, this one might take a while... |")
    print("----------------------------------------------------")
    print('{:40}{:20}{}'.format('Register name', 'Value', 'Description\n'))
    data = heru.dump_holding_register()
    unit = ['  ','°C','%','%','%','%','%','  ','  ','°C','°C','  ','0.1°C','°C','°C','  ','°C','  ','  ',' x 10 PPM CO2',' min','% points / hour','  ','  ','% points / hour','  ',' min',' min','°C','°C','  ','  ','  ','  ','  ','  ','  ','  ','  ','% points','  ','  ','  ',' months','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','°C','  ','  ','  ','  ','  ','  ','  ','  ','  ','°C','  ','  ','  ','  ','  ','  ','  ','  ','  ','°C','  ','  ','  ','  ','  ','  ','  ','  ','  ','°C','  ','  ','  ','  ','  ','  ','  ','  ','  ','°C','  ','  ',' x 0.1V',' s']
    description = ['0 = Off, 1 = Min, 2 = Std, 3 = Mod, 4 = Max. Used if no weektimer is active, AC fans only.','  ','  ','  ','Fan speed when min speed used, for example away-mode','Fan speed when mod speed used, for example boost','Fan speed when max speed used, for example boost','Readable, value has no meaning','Readable, value has no meaning','  ','  ','0 = supply, 1 = exhaust, 2 = room.','  ','  ','  ','0 = no, 1 = yes','  ','Readable, value has no meaning','Readable, value has no meaning','Carbon dioxide level limit.','Boosting interval, AC fans only.','Boosting ramp, EC fans only.','Relative humidity limit, in % RH units.','Boosting interval in minutes, AC fans only.','Boosting ramp, EC fans only.','3 = Mod, 4 = Max.','  ','  ','  ','Must be greater than limit A above.','0 = none, 1 = normally open, 2 = normally closed','Readable, value has no meaning','0 = switch, 1 = -50..50 Pa, 2 = 0..100 Pa, 3 = 0..150 Pa, 4 = 0..300 Pa, 5 = 0..500 Pa, 6 =','0..1000 Pa, 7 = 0..1600 Pa, 8 = 0..2500 Pa','0 = no, 1 = yes','0 = no, 1 = yes','0 = Monday, 1 = Tuesday … 6 = Sunday.','  ','  ','0 = off, 5 to 50 = allowed power increase in %-units. Writing 5 or less equals 0.','Readable, value has no meaning','Readable, value has no meaning','Readable, value has no meaning','Filter timer in months. 0 = off, 6-12 time in months (30 days). Writing 5 or less equals 0.','Bit mask: bit 0 = Fire, bit 1 = Rotor, bit 2 = 0, bit 3 = Freeze, bit 4 = Low supply temperature, bit 5 = Low rotor temperature, bit 6 = 0,bit 7 = 0','Bit mask: bit 0 = Sensor open, bit 1 = Sensor shorted, bit 2 = Pulser, bit 3 = Supply fan, bit 4 = Exhaust fan, bit 5 = Supply filter, bit 6 = Exhaust filter, bit 7 = Filter timer','Readable, value has no meaning','Readable, value has no meaning','Readable, value has no meaning','0 = no, 1 = yes','0 = no, 1 = yes','0 = no, 1 = yes','0 = right, 1 = left','Readable, value has no meaning','Readable, value has no meaning','Readable, value has no meaning','Readable, value has no meaning','Readable, value has no meaning','Readable, value has no meaning','0 = Monday, 1 = Tuesday ... 6 = Sunday. Reading this copies time to read/write buffer.','  ','  ','Writing this writes time from read/write buffer','Readable, value has no meaning','Readable, value has no meaning','Readable, value has no meaning','Readable, value has no meaning','Readable, value has no meaning','0 = no, 1 = yes','  ','  ','  ','  ','Bit mask: bit 0 = Monday, bit 6 = Sunday.','  ','1 = Min, 2 = Std, 3 = Mod, 4 = Max.','Readable, value has no meaning','Readable, value has no meaning','Readable, value has no meaning','  ','  ','  ','  ','Bit mask: bit 0 = Monday, bit 6 = Sunday.','  ','1 = Min, 2 = Std, 3 = Mod, 4 = Max.','Readable, value has no meaning','Readable, value has no meaning','Readable, value has no meaning','  ','  ','  ','  ','Bit mask: bit 0 = Monday, bit 6 = Sunday.','1 = Min, 2 = Std, 3 = Mod, 4 = Max.','Readable, value has no meaning','Readable, value has no meaning','Readable, value has no meaning','  ','  ','  ','  ','  ','Bit mask: bit 0 = Monday, bit 6 = Sunday.','  ','1 = Min, 2 = Std, 3 = Mod, 4 = Max.','Readable, value has no meaning','Readable, value has no meaning','Readable, value has no meaning','  ','  ','  ','  ','Bit mask: bit 0 = Monday, bit 6 = Sunday.','  ','1 = Min, 2 = Std, 3 = Mod, 4 = Max.','0 = AC fans, 1 = EC fans with tacho, 2 = EC fans with alarm output','Voltage on fan when 100% power is applied.','Rotor pulsing period.']
    text = ['User fan speed','Temperature setpoint','Supply fan speed, EC','Exhaust fan speed, EC','Min exhaust fan speed, EC','Mod exhaust fan speed, EC','Max exhaust fan speed, EC','RFU','RFU','Min supply temperature','Max supply temperature','Regulation mode','SNC indoor-outdoor diff. Limit','SNC exhaust low limit','SNC exhaust high limit','SNC enable','Freeze protection limit temperature','RFU','RFU','CO2 limit','CO2 interval','CO2 ramp','RH limit','RH interval','RH ramp','Boost speed','Boost duration','Overpressure duration','Supply cold limit A','Supply cold limit B','Fire sensor type','RFU','Supply pressure sensor type','Exhaust pressure sensor type','Supply pressure switch present','Exhaust pressure switch present','Filter measurement, weekday','Filter measurement, hour','Filter measurement, minute','Filter speed increase','RFU','RFU','RFU','Filter change period','Alarm relay option 1','Alarm relay option 2','RFU','RFU','RFU','Water heater connected','Electric heater connected','Cooler connected','Flow direction','RFU','RFU','RFU','RFU','RFU','RFU','Clock, Weekday','Clock, Hours','Clock, Minutes','Clock, Seconds','RFU','RFU','RFU','RFU','RFU','Weektimer enable','WT1 on hour','WT1 on minute','WT1 off hour','WT1 off minute','WT1 weekdays','WT1 temperature setpoint','WT1 fan speed','RFU','RFU','RFU','WT2 on hour','WT2 on minute','WT2 off hour','WT2 off minute','WT2 weekdays','WT2 temperature setpoint','WT2 fan speed','RFU','RFU','RFU','WT3 on hour','WT3 on minute','WT3 off hour','WT3 off minute','WT3 weekdays','WT3 temperature setpoint','WT3 fan speed','RFU','RFU','RFU','WT4 on hour','WT4 on minute','WT4 off hour','WT4 off minute','WT4 weekdays','WT4 temperature setpoint','WT4 fan speed','RFU','RFU','RFU','WT5 on hour','WT5 on minute','WT5 off hour','WT5 off minute','WT5 weekdays','WT5 temperature setpoint','WT5 fan speed','Fan type','EC fan max speed','Rotor pulsing period']

    for line in zip(text, data, unit, description):
        print('{:40}{}{:20}{}'.format(*line))
    
    #print( 'DONE!' )

pass
