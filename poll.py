#!/usr/bin/python
# -*- coding=utf-8 -*-
from I2C_BUS import *
from BillValidator import *
import time

iface=i2c_bus("./config/lib/libi2c.so","/dev/i2c-1",4)
billvalidator=bill_validator(iface,3,1)
billvalidator.Poll()
time.sleep(1)
billvalidator.stack()
billvalidator.sendACK()