#!/usr/bin/python
# -*- coding=utf-8 -*-
from I2C_BUS import *
from BillValidator import *
import time

iface=i2c_bus("./config/lib/libi2c.so","/dev/i2c-1",4)
billvalidator=bill_validator(iface,3,1,50)
billvalidator.reset()
#billvalidator.enable(0xff,0xff,0xff,0xff,0xff,0xff)
#billvalidator.Poll()
#time.sleep(0.2)
#billvalidator.Poll()
#time.sleep(0.2)
#billvalidator.Poll()
#time.sleep(0.2)
#billvalidator.Poll()
#time.sleep(0.2)
#billvalidator.Poll()
#time.sleep(0.2)
#billvalidator.Poll()

def receiving_bills():
	iface.receive_req(6,2,0)

	billvalidator.enable(0xff,0xff,0xff,0xff,0xff,0xff)
	time.sleep(0.2)
	billvalidator.Poll()
	while (1):
		fl=iface.receive_req(6,1,1)
		if(fl[0]==0 and fl[3]==ord('D')):
			billvalidator.disable()
			time.sleep(0.02)	
			billvalidator.Poll()
			print 'current summ : ',billvalidator.cursum
			return billvalidator.cursum
		time.sleep(0.2)	
		billvalidator.Poll()
		billvalidator.sendACK()

receiving_bills()