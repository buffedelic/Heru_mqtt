#!/usr/bin/env python3

import minimalmodbus

class HeruFTX( minimalmodbus.Instrument ):
    
    def __init__(self, portname, slaveaddress):
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)
    
    def coil_status(self, human=False):
        number_registers = 6
        i = 0
        l = []
        while i < number_registers:
            value = 3
            while value is 3:
                try:
                    value = self.read_bit(i, functioncode=1)
                    if human:
                        if value == 0: #format value to human language
                            value = "Off"
                        else:
                            value = "On"
                except:
                    pass
            l.append(value)
            i = i + 1
        return l
    
    def get_coil_status(self, register):
        return self.read_bit(register-1, functioncode=1)
    
    def set_coil_status(self, register, value=None):

        ### Functioncode 5 ########
        #0x00001 Unit on
        #0x00002 Overpressure mode
        #0x00003 Boost mode
        #0x00004 Away mode
        #0x00005 Clear Alarms
        #0x00006 Reset filter timer
        ###########################
        try:    
            if value.lower() == "off": #format value from human language
                value = 0
            elif value.lower() == "on":
                value = 1
        except:
            pass

        # Check if state change is needed
        if self.read_bit(register -1, functioncode=1) is not value:
            try:
                self.write_bit(register -1, value, functioncode=5)
            except:
                print("Failed to communicate with instrument")


    def input_status(self, human=False):
        number_registers = 34
        i = 0
        l = []

        while i < number_registers:
            value = 3
            while value is 3:
                try:
                    value = self.read_bit(i, functioncode=2)
                    if human:
                        if value == 0: #format value to human language
                            value = "Off"
                        else:
                            value = "On"
                except:
                    pass
            l.append(value)
            i = i + 1
            if i == 4:      #if register 1x00004 is done, jump to 1x00010. (from heru modbus list)
                i = 9

        return l

    def  input_register(self):
        number_registers = 33

        l = None
        while l is None:
            try:
                l = self.read_registers(0, number_registers, functioncode=4)
            except:
                pass

        return l

    def  holding_register(self):
        number_registers = 116

        l = None
        while l is None:
            try:
                l = self.read_registers(0, number_registers, functioncode=3)
            except:
                pass
        self.write_register(999, 1991)
        number_registers = 3
        s = None
        while s is None:
            try:
                s = self.read_registers(1000, number_registers, functioncode=3)
            except:
                pass
        self.write_register(999, 1191)
        l = l + s
        return l