#!/usr/bin/python
# -*- coding=utf-8 -*-

import time
import math

class bill_validator:
	
	def __init__(self,interface,addrDev,numch,maxSum):
		self.__interface=interface
		#self.__interface.set_settings_port(numch,14,8)
		self.__addrDev=addrDev
		self.__numch=numch
		self.denom_table=[]
		self.cursum=0
		self.__maxsum=maxSum
		self.__tx_mess=bytearray()
		self.__rx_mess=bytearray()
		self.isEnable=0
		self.inEnable=0
		self.inDisable=0
		print self.__interface
		
		
		
##############################################################################################################
# Функция высчитывает контрольную сумму
##############################################################################################################
	
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
		
		

##############################################################################################################
# Функция передает пакет данных купюроприемнику
##############################################################################################################
	
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
		
		
		
##############################################################################################################
# Функция перезагружает купюроприемник
##############################################################################################################	
		
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
		
		if(len(answer)==1 and answer[0]==0x30):
			print 'BillValidator.getStatus()::ILLEGAL COMMAND'
			print '/BillValidator.reset()>'
			return -1
		print '/BillValidator.reset()>'
		return answer



##############################################################################################################
# Функция получение статуса купюроприемника
##############################################################################################################	

	def getStatus(self):
		print '<BillValidator.getStatus()'
		
		self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x31])==-1):
			print "BillValidator.getStatus()::Error : Can\'t transmit request."
			print '/BillValidator.getStatus()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.getStatus()::Error : Can\'t get an answer.'
			print '/BillValidator.getStatus()>'
			return -1
		if(len(answer)==1 and answer[0]==0x30):
			print 'BillValidator.getStatus()::ILLEGAL COMMAND'
			print '/BillValidator.getStatus()>'
			return -1
		print '/BillValidator.getStatus()>'
		return answer
			


##############################################################################################################
# Функция установки режима безопасности
##############################################################################################################	

	def setSecurity(self,y1,y2,y3):
		print '<BillValidator.setSecurity()'
		
		self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x31,y1,y2,y3])==-1):
			print "BillValidator.setSecurity()::Error : Can\'t transmit request."
			print '/BillValidator.setSecurity()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.setSecurity()::Error : Can\'t get an answer.'
			print '/BillValidator.setSecurity()>'
			return -1
		if(len(answer)==1 and answer[0]==0x30):
			print 'BillValidator.setSecurity()::ILLEGAL COMMAND'
			print '/BillValidator.setSecurity()>'
			return -1
		print '/BillValidator.setSecurity()>'
		return answer

			

##############################################################################################################
# Функция разрешенния типа купюры
##############################################################################################################	

	def enable(self,y1,y2,y3,y4,y5,y6):
		print '<BillValidator.enable()'
		
		self.inEnable=0
		self.__interface.receive_req(self.__numch,2,0)
		self.__isEnable=1
		self.__inEnable=1
		if(self.__request([0x34,y1,y2,y3,y4,y5,y6])==-1):
			print "BillValidator.enable()::Error : Can\'t transmit request."
			print '/BillValidator.enable()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.enable()::Error : Can\'t get an answer.'
			print '/BillValidator.enable()>'
			return -1
		if(len(answer)==1 and answer[0]==0x30):
			print 'BillValidator.enable()::ILLEGAL COMMAND'
			print '/BillValidator.enable()>'
			return -1
		print '/BillValidator.enable()>'	
		return answer
		


##############################################################################################################
# Функция разрешенния типа купюры
##############################################################################################################	

	def disable(self):
		print '<BillValidator.disable()'
		
		self.inDisable=0
		self.__interface.receive_req(self.__numch,2,0)
		self.__isEnable=0
		self.__inDisable=1
		if(self.__request([0x34,0,0,0,0,0,0])==-1):
			print "BillValidator.disable()::Error : Can\'t transmit request."
			print '/BillValidator.disable()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.disable()::Error : Can\'t get an answer.'
			print '/BillValidator.disable()>'
			return -1
		if(len(answer)==1 and answer[0]==0x30):
			print 'BillValidator.disable()::ILLEGAL COMMAND'
			print '/BillValidator.disable()>'
			return -1
		print '/BillValidator.disable()>'	
		return answer


##############################################################################################################
# Функция принятия купюры
##############################################################################################################	
		
	def stack(self):
		print '<BillValidator.stack()'
		
		self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x35])==-1):
			print "BillValidator.stack()::Error : Can\'t transmit request."
			print '/BillValidator.stack()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.stack()::Error : Can\'t get an answer.'
			print '/BillValidator.stack()>'
			return -1
		if(len(answer)==1 and answer[0]==0x30):
			print 'BillValidator.stack()::ILLEGAL COMMAND'
			print '/BillValidator.stack()>'
			return -1
		print '/BillValidator.stack()>'
		return answer
	
	
	
##############################################################################################################
# Функция возврата купюры
##############################################################################################################	

	def return_(self):
		print '<BillValidator.return_()'

		self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x36])==-1):
			print "BillValidator.return()::Error : Can\'t transmit request."
			print '/BillValidator.return_()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.return()::Error : Can\'t get an answer.'
			print '/BillValidator.return_()>'
			return -1
		if(len(answer)==1 and answer[0]==0x30):
			print 'BillValidator.return_()::ILLEGAL COMMAND'
			print '/BillValidator.return_()>'
			return -1
		print '/BillValidator.return_()>'
		return answer
	
	
	
##############################################################################################################
# Функция идентификации купюроприемника
##############################################################################################################
	
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
		if(len(answer)==1 and answer[0]==0x30):
			print 'BillValidator.identification()::ILLEGAL COMMAND'
			print '/BillValidator.identification()>'
			return -1
		print '/BillValidator.identification()>'
		return answer
	
	
	
##############################################################################################################
# Функция удержания купюры в эскроу
##############################################################################################################

	def hold(self):
		print '<BillValidator.hold()'
	
		self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x38])==-1):
			print "BillValidator.hold()::Error : Can\'t transmit request."
			print '/BillValidator.hold()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.hold()::Error : Can\'t get an answer.'
			print '/BillValidator.hold()>'
			return -1
		if(len(answer)==1 and answer[0]==0x30):
			print 'BillValidator.hold()::ILLEGAL COMMAND'
			print '/BillValidator.hold()>'
			return -1
		print '/BillValidator.hold()>'
		return answer
	
	
	
##############################################################################################################
# Функция установка параметров штрих кода
##############################################################################################################

	def setBarcodeParam(self,y1,y2):
		print '<BillValidator.setBarcodeParam()'
	
		self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x39,y1,y2])==-1):
			print "BillValidator.setBarcodeParam()::Error : Can\'t transmit request."
			print '/BillValidator.setBarcodeParam()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.setBarcodeParam()::Error : Can\'t get an answer.'
			print '/BillValidator.setBarcodeParam()>'
			return -1
		if(len(answer)==1 and answer[0]==0x30):
			print 'BillValidator.setBarcodeParam()::ILLEGAL COMMAND'
			print '/BillValidator.setBarcodeParam()>'
			return -1
		print '/BillValidator.setBarcodeParam()>'
		return answer
	
	

##############################################################################################################
# Функция 
##############################################################################################################

	def extrBarcodeData(self):
		print '<BillValidator.extrBarcodeData()'
	
		self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x3A])==-1):
			print "BillValidator.extrBarcodeData()::Error : Can\'t transmit request."
			print '/BillValidator.extrBarcodeData()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.extrBarcodeData()::Error : Can\'t get an answer.'
			print '/BillValidator.extrBarcodeData()>'
			return -1
		if(len(answer)==1 and answer[0]==0x30):
			print 'BillValidator.extrBarcodeData()::ILLEGAL COMMAND'
			print '/BillValidator.extrBarcodeData()>'
			return -1
		print '/BillValidator.extrBarcodeData()>'
		return answer
	
	
	
##############################################################################################################
# Функция получения таблицы деноминаций купюроприемника
##############################################################################################################

	def getBillTable(self):
		print '<BillValidator.getBillTable()'
	
		self.__interface.receive_req(self.__numch,2,0)
		self.denom_table=[]
		#self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x41])==-1):
			print "BillValidator.getBillTable()::Error : Can\'t transmit request."
			print '/BillValidator.getBillTable()>'
			return -1
		res=self.getAnsw()
		if(res==-1):
			print 'BillValidator.extrBarcodeData()::Error : Can\'t get an answer.'
			print '/BillValidator.getBillTable()>'
			return -1
		
		if(len(res)==1 and res[0]==0x30):
			print 'BillValidator.getStatus()::ILLEGAL COMMAND'
			return -1
			
		for j in range(0,120,5):
			value=res[j]*math.pow(10,res[j+4])
			print 'self.__denomTable[',j/5,']	',value
			self.denom_table.append(value)
		print '/BillValidator.getBillTable()>'
		return 1
		
	
	
##############################################################################################################
# Функция получения контрольной суммы прошивки купюроприемника
##############################################################################################################

	def getCRC32(self):
		print '<BillValidator.getCRC32()'
		
		self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x51])==-1):
			print "BillValidator.getCRC32()::Error : Can\'t transmit request."
			print '/BillValidator.getCRC32()>'
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.getCRC32()::Error : Can\'t get an answer.'
			print '/BillValidator.getCRC32()>'
			return -1
		if(len(answer)==1 and answer[0]==0x30):
			print 'BillValidator.getCRC32()::ILLEGAL COMMAND'
			print '/BillValidator.getCRC32()>'
			return -1
		print '/BillValidator.getCRC32()>'
		return answer
		
	

##############################################################################################################
# Функция отпраки ACK пакета
##############################################################################################################	
	def sendACK(self):
		print '<BillValidator.sendACK()'
		
		self.__interface.receive_req(self.__numch,2,0)
		if(self.__request([0x00])==-1):
			print "BillValidator.reset()::Error : Can\'t transmit request."
			print '/BillValidator.sendACK()>'
			return -1
		print '/BillValidator.sendACK()>'
		return 1
		
		
		
##############################################################################################################
# Функция отправки NAK пакета
##############################################################################################################
		
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
		

##############################################################################################################
# Функция Пуллинга купюроприемника
##############################################################################################################

	def Poll(self):
		print "<BillValidator.Poll()"
	
		self.__interface.receive_req(self.__numch,2,0)															# Очистка буфера приемника
		if(self.__request([0x33])==-1):
			print "BillValidator.reset()::Error : Can\'t transmit request."
			return -1
		answer=self.getAnsw()
		if(answer==-1):
			print 'BillValidator.Poll()::Error: Can\'t get an answer'
			return -1
		z1=answer[0]
		print "z1	=	",z1
		if((z1==0x10) or (z1==0x11) or (z1==0x12)):
			self.reset()
			return 1
			
		if(z1==0x13):
			print "BillValidator.Poll::Initialize"
			if(self.identification()==-1):
				return -1
			time.sleep(0.2)
			if(self.getBillTable()==-1):
				return -1
			return 1
			
		if(z1==0x14):
			if(self.inDisable==1):
				self.disable()
				print "BillValidator.Poll::Disable"
			return 3
			
		if((z1==0x15) or (z1==0x17) or (z1==0x18)):
			print "BillValidator.Poll::Enable"
			return
			
		if(z1==0x19):
			if(self.inEnable==1):
				self.enable(0xff,0xff,0xff,0xff,0xff,0xff)
				print "BillValidator.Poll::Enable"
			return 1
			
		if(z1==0x1A):
			print "BillValidator.Poll::Holding"
			return 1
			
		if(z1==0x1B):
			z2=answer[1]
			print 'z2:',z2
			print "BillValidator.Poll::Device Busy"
			return 1
			
		if(z1==0x1C):
			z2=answer[1]
			print 'z2:',z2
			print "BillValidator.Poll::rejection"
			return 1
			
		if(z1==0x41):
			print "BillValidator.Poll::Drop Cassette Full"
			return 1
			
		if(z1==0x42):
			print "BillValidator.Poll::Drop Cassette out of position"
			return 1
			
		if(z1==0x43):
			print "BillValidator.Poll::Validator Jammed"
			return 1
			
		if(z1==0x44):
			print "BillValidator.Poll::Drop Cassette Jammed"
			return 1
			
		if(z1==0x45):
			print "BillValidator.Poll::Cheated"
			return 1
			
		if(z1==0x46):
			print "BillValidator.Poll::Pause"
			return 1
			
		if(z1==0x47):
			z2=answer[1]
			print 'z2:',z2
			print "BillValidator.Poll::Failure"
			return 1
			
		if(z1==0x80):
			z2=answer[1]
			print 'z2:',z2
			sum=self.denom_table[z2]
			if((self.__isEnable==1) and (self.cursum+sum < self.__maxsum or self.cursum==0)):
				self.stack()
				self.cursum+=sum
			else:
				self.return_()
			print "BillValidator.Poll::Escrow position"
			return
		if(z1==0x81):
			print "BillValidator.Poll::Bill stacked"
			return
		if(z1==0x82):
			print "BillValidator.Poll::Bill returned"
			return

		
	
		
		