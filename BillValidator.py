#!/usr/bin/python
# -*- coding=utf-8 -*-

import time
import math

class bill_validator:
	
	def __init__(self,interface,addrDev,numch):
		self.__interface=interface
		self.__interface.set_settings_port(1,14,8)
		self.__addrDev=addrDev
		self.__numch=numch
		self.denom_table=[]
		self.cursum=0
		self.maxsum=0
		self.__tx_mess=bytearray()
		self.__rx_mess=bytearray()
		self.isEnable=0
		self.isDisable=0
		print self.__interface
		
##==================================================================================================================	
	
	def calc_crc(self,data):
		crc=0
		for i in data:
			crc^=i
			for j in range(8):
				if(crc & 0x0001):
					crc >>=1
					crc ^=0x8408
				else: crc >>=1
		return crc
		
##==================================================================================================================
	
	def __request(self,data):
		print "BillValidator::__request()\n"
		
		self.__tx_mess=bytearray()
		self.__tx_mess.append(0x02)
		self.__tx_mess.append(self.__addrDev)
		self.__tx_mess.append(len(data)+5)
		self.__tx_mess.extend(data)
		crc=self.calc_crc(self.__tx_mess)
		print crc
		self.__tx_mess.append(crc%0x100)
		self.__tx_mess.append((crc/0x100)&0xff)
		for i in range(len(self.__tx_mess)):
			print "BILL VALIDATOR CMD byte[",i,']',self.__tx_mess[i]
		
		if(self.__interface.transmit_req(self.__numch,self.__tx_mess,len(self.__tx_mess))==-1):
			return -1
		return 1
		
##==================================================================================================================
		
		
		
	def reset(self):
		print '<BillValidator.reset()'
		
		self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x30])==-1):
			print "BillValidator.reset()::Error : Can\'t transmit request."
			print '/BillValidator.reset()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.reset()::Error : Can\'t get an answer.'
			print '/BillValidator.reset()>'
			return -1
		print '/BillValidator.reset()>'
		return answer


	def getStatus(self):
		print '<BillValidator.getStatus()'
		
		if(self.__request([0x31])==-1):
			print "BillValidator.getStatus()::Error : Can\'t transmit request."
			print '/BillValidator.getStatus()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.getStatus()::Error : Can\'t get an answer.'
			print '/BillValidator.getStatus()>'
			return -1
		print '/BillValidator.getStatus()>'
		return answer
			

	def setSecurity(self,y1,y2,y3):
		print '<BillValidator.setSecurity()'
		
		if(self.__request([0x31,y1,y2,y3])==-1):
			print "BillValidator.setSecurity()::Error : Can\'t transmit request."
			print '/BillValidator.setSecurity()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.setSecurity()::Error : Can\'t get an answer.'
			print '/BillValidator.setSecurity()>'
			return -1
		print '/BillValidator.setSecurity()>'
		return answer

			
	def enable(self,y1,y2,y3,y4,y5,y6):
		print '<BillValidator.enable()'
		#self.wEnable=0
		if(self.__request([0x34,y1,y2,y3,y4,y5,y6])==-1):
			print "BillValidator.enable()::Error : Can\'t transmit request."
			print '/BillValidator.enable()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.enable()::Error : Can\'t get an answer.'
			print '/BillValidator.enable()>'
			return -1
		print '/BillValidator.enable()>'	
		return answer
		
		
		
	def stack(self):
		print '<BillValidator.stack()'
		
		if(self.__request([0x35])==-1):
			print "BillValidator.stack()::Error : Can\'t transmit request."
			print '/BillValidator.stack()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.stack()::Error : Can\'t get an answer.'
			print '/BillValidator.stack()>'
			return -1
		print '/BillValidator.stack()>'
		return answer
	
	
	def return_(self):
		print '<BillValidator.return_()'	
	
		if(self.__request([0x36])==-1):
			print "BillValidator.return()::Error : Can\'t transmit request."
			print '/BillValidator.return_()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.return()::Error : Can\'t get an answer.'
			print '/BillValidator.return_()>'
			return -1
		print '/BillValidator.return_()>'
		return answer
	
	
	def identification(self):
		print '<BillValidator.identification()'
	
		self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x37])==-1):
			print "BillValidator.identification()::Error : Can\'t transmit request."
			print '/BillValidator.identification()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.identification()::Error : Can\'t get an answer.'
			print '/BillValidator.identification()>'
			return -1
		print '/BillValidator.identification()>'
		return answer
	
	
	def hold(self):
		print '<BillValidator.hold()'
	
		if(self.__request([0x38])==-1):
			print "BillValidator.hold()::Error : Can\'t transmit request."
			print '/BillValidator.hold()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.hold()::Error : Can\'t get an answer.'
			print '/BillValidator.hold()>'
			return -1
		print '/BillValidator.hold()>'
		return answer
	
	
	def setBarcodeParam(self,y1,y2):
		print '<BillValidator.setBarcodeParam()'
	
		if(self.__request([0x39,y1,y2])==-1):
			print "BillValidator.setBarcodeParam()::Error : Can\'t transmit request."
			print '/BillValidator.setBarcodeParam()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.setBarcodeParam()::Error : Can\'t get an answer.'
			print '/BillValidator.setBarcodeParam()>'
			return -1
		print '/BillValidator.setBarcodeParam()>'
		return answer
	
	
	def extrBarcodeData(self):
		print '<BillValidator.extrBarcodeData()'
	
		if(self.__request([0x3A])==-1):
			print "BillValidator.extrBarcodeData()::Error : Can\'t transmit request."
			print '/BillValidator.extrBarcodeData()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.extrBarcodeData()::Error : Can\'t get an answer.'
			print '/BillValidator.extrBarcodeData()>'
			return -1
		print '/BillValidator.extrBarcodeData()>'
		return answer
	
	def getBillTable(self):
		print '<BillValidator.getBillTable()'
	
		denomTable=[]
		self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x41])==-1):
			print "BillValidator.getBillTable()::Error : Can\'t transmit request."
			print '/BillValidator.getBillTable()>'
			return -1
		res=self.getAnsw()
		if(res==-1):
			print 'BillValidator.extrBarcodeData()::Error : Can\'t get an answer.'
			print '/BillValidator.getBillTable()>'
			return -1
		for j in range(0,120,5):
			value=res[j]*math.pow(10,res[j+4])
			print 'self.__denomTable[',j/5,']	',value
			denomTable.append(value)
		print '/BillValidator.getBillTable()>'
		return denomTable
		
	
	def getCRC32(self):
		print '<BillValidator.getCRC32()'
		
		if(self.__request([0x51])==-1):
			print "BillValidator.getCRC32()::Error : Can\'t transmit request."
			print '/BillValidator.getCRC32()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.getCRC32()::Error : Can\'t get an answer.'
			print '/BillValidator.getCRC32()>'
			return -1
		print '/BillValidator.getCRC32()>'
		return answer
		
		
	def sendACK(self):
		print '<BillValidator.sendACK()'
		
		if(self.__request([0x00])==-1):
			print "BillValidator.reset()::Error : Can\'t transmit request."
			print '/BillValidator.sendACK()>'
			return -1
		print '/BillValidator.sendACK()>'
		return 1
		
		
	def sendNAK(self):
		print '<BillValidator.sendNAK()'
	
		if(self.__request([0xff])==-1):
			print "BillValidator.reset()::Error : Can\'t transmit request."
			print '/BillValidator.sendNAK()>'
			return -1
		print '/BillValidator.sendNAK()>'
		return 1
		
	
	
##############################################################################################################
# Функция получает ответ на команду если удачно возвращает данные иначе -1
##############################################################################################################
	
	def getAnsw(self):
		print '<BillValidator.getAnsw()'
		answer=bytearray()
		
		startByte=self.get_byte(100)
		if(startByte==-1):
			print 'BillValidator.getAnsw(): Error getting byte()'
			print '/BillValidator.getAnsw()>'
			return -1
		
		if(startByte!=0x02):
			print 'bill validator::getAnsw():not start byte'
			print '/BillValidator.getAnsw()>'
			return -1
		answer.append(startByte)
		
		addrByte=self.get_byte(10)
		if(startByte==-1):
			print 'BillValidator.getAnsw(): Error getting byte()' 
			print '/BillValidator.getAnsw()>'
			return -1
		if(addrByte!=0x03):
			print 'bill validator::getAnsw():error address'
			print '/BillValidator.getAnsw()>'
			return -1
		answer.append(addrByte)
		
		lenByte=self.get_byte(10)
		if(startByte==-1):
			print 'BillValidator.getAnsw(): Error getting byte()'
			print '/BillValidator.getAnsw()>'
			return -1
		answer.append(lenByte)
		
		time.sleep(lenByte*0.0005)
		
		respData=self.__interface.receive_req(self.__numch,1,lenByte-3)
		if(respData==-1):
			print 'BillValidator.getAnsw()::Error: can''t getting answer'
			return -1
		answer.extend(respData[3:])
		crc=self.calc_crc(answer)
		if(crc!=0):
			print "BillValidator.getAnsw()::Error: Incorrect checksum"
			print '/BillValidator.getAnsw()>'
			return -1
		print '/BillValidator.getAnsw()>'
		return answer[3:-2]


##############################################################################################################
# Функция запрашивает считывает один байт с СOM порта купюроприемника если удачно возвращает байт если нет -1
##############################################################################################################

	def get_byte(self,timeout):
		print "<BillValidator.get_byte()" 
		
		for i in range(timeout):
			time.sleep(0.001)
			rx_byte=self.__interface.receive_req(self.__numch,1,1)
			if(rx_byte==-1):
				print "BillValidator.get_byte():Error getting byte"
				return -1
			if(rx_byte[0]==0):
				print "/BillValidator.get_byte()>"
				return rx_byte[3]
			else	:
				print 'number error - ', rx_byte[0]
				continue
		print "/BillValidator.get_byte()>"
		return -1
		


	def Poll(self):
		self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x33])==-1):
			raise ValueError("BillValidator.reset()::Error : Can\'t transmit request.")
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.Poll()::Error: Can\'t get an answer'
			return
		self.sendACK
		z1=answer[0]
		#z2=answer[1]
		print "z1	=	",z1
		#print "z2	=	",z2
		if((z1==0x10) or (z1==0x11) or (z1==0x12)):
			self.reset()
			return
		if(z1==0x13):
			print "Initialize"
			self.identification()
			self.getBillTable()
			return
		if((z1==0x14) or (z1==0x15) or (z1==0x17) or (z1==0x18)):
			print "Enable"
			return
		if(z1==0x19):
			print "Disable"
			return
		if(z1==0x1A):
			print "Holding"
			return
		if(z1==0x1B):
			print "Device Busy"
			return
		if(z1==0x1C):
			print "rejection"
			return
		if(z1==0x41):
			print "Drop Cassette Full"
			return
		if(z1==0x42):
			print "Drop Cassette out of position"
			return
		if(z1==0x43):
			print "Validator Jammed"
			return
		if(z1==0x44):
			print "Drop Cassette Jammed"
			return
		if(z1==0x45):
			print "Cheated"
			return
		if(z1==0x46):
			print "Pause"
			return
		if(z1==0x47):
			print "Failure"
			return
		if(z1==0x80):
			print "Escrow position"
			return
		if(z1==0x81):
			print "Bill stacked"
			return
		if(z1==0x82):
			print "Bill returned"
			return
		#if(answer[3
		
	
		
		