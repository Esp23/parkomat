#!/usr/bin/python
# -*- coding=utf-8 -*-
from I2C_BUS import *
from BillValidator import *
import time

iface=i2c_bus("./config/lib/libi2c.so","/dev/i2c-1",4)
#byte=iface.transmit_req(6,[0x10],1)
#byte=iface.receive_req(6,1,1)
#print byte
#iface.close()
billvalidator=bill_validator(iface,3,1)
#billvalidator.getBillTable()
billvalidator.reset()
#billvalidator.getBillTable()
#billvalidator.getBillTable()
billvalidator.enable(0xff,0xff,0xff,0xff,0xff,0xff)
billvalidator.Poll()
