#!/usr/bin/env python3

import minimalmodbus
#print(minimalmodbus._get_diagnostic_string())


class HeruFTX(minimalmodbus.Instrument):
    """
    Heru modbus wrapper
    Communicates trough modbus protocol with Östberg Heru Products.
    For further information read on https://se.ostberg.com/produkter/
    """

    def __init__(self, portname, slaveaddress):
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)
        self.mode = minimalmodbus.MODE_RTU
        self.serial.stopbits = 1
        self.serial.timeout = 0.3  # Might need adjustment for different hardware (0.5)
        self.debug = False
        self.precalculate_read_size = False

    def dump_coil_status(self, human=False):
        number_registers = 6
        i = 0
        data = []
        while i < number_registers:
            value = 3
            while value == 3:
                try:
                    value = self.read_bit(i, functioncode=1)
                    if human:
                        if value == 0:  # format value to human language
                            value = "Off"
                        else:
                            value = "On"
                except:
                    #print("!!!!!!!!!!!!!!!!!!!!!!!!")
                    pass
            data.append(value)
            i = i + 1
        return data

    def get_coil_status(self, register):
        try:
            return self.read_bit(register -1, functioncode=1)
        except:
            return None

    def set_coil_status(self, register, value=None):
        """
        Used to set set register takes, handle both 1 and 0 aswell as litteral "on" and "off"
        """
        try:
            if value.lower() == "off":  # format value from human language
                value = 0
            elif value.lower() == "on":
                value = 1
        except:
            pass

        try:
            self.write_bit(register -1, value, functioncode=5)
        except:
            print("Failed to communicate with instrument")

    def dump_input_status(self, human=False):
        number_registers = 34
        i = 0
        data = []

        while i < number_registers:
            value = 3
            while value == 3:
                try:
                    value = self.read_bit(i, functioncode=2)
                    if human:
                        if value == 0:  # format value to human language
                            value = "Off"
                        else:
                            value = "On"
                except:
                    pass
            data.append(value)
            i = i + 1
            if i == 4:      # if register 1x00004 is done, jump to 1x00010. (from heru modbus list)
                i = 9

        return data

    def get_input_status(self, register):
        try:
            return self.read_bit(register -1 , functioncode=2)
        except:
            return None

    def dump_input_register(self):
        number_registers = 33

        data = None
        while data is None:
            try:
                data = self.read_registers(0, number_registers, functioncode=4)
            except:
                pass

        return data

    def get_input_register(self, register):
        try:
            return self.read_bit(register -1, functioncode=4)
        except:
            return None

    def dump_holding_register(self):
        number_registers = 116

        data = None
        while data is None:
            try:
                data = self.read_registers(0, number_registers, functioncode=3)
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
        data = data + s
        return data

    def get_holding_register(self, register):
        try:
            return self.read_bit(register -1 , functioncode=3)
        except:
            return None
