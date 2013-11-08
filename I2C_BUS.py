#!/usr/bin/python
# -*- coding=utf-8 -*-

from ctypes import *
from array import array
from types import *

version=""
array_byte=c_ubyte*512

def lo8(data):
	res=c_ushort()
	res.value=(data & 0xff)
	return res.value

def hi8(data):
	res=c_ushort()
	res.value=(data>>8)
	return res.value
							

##################################################################################
# Base class for communication with i2c bus
#
##################################################################################

class i2c_bus:
	
	def __init__(self,libName,devName,assignAddr):

		self.__tx_buff=array_byte()
		self.__rx_buff=array_byte()
		
		#self.__full_tx_buff=[]
		self.__full_rx_buff=[]
		
		self.__lib_name=libName
		self.__assign_addr=assignAddr
		self.__dev_name=devName

		self.__count=0

		self.__size_rx_packet=0
		self.__size_tx_packet=0

		self.dl=cdll.LoadLibrary(self.__lib_name)
		
		fd=self.dl.open_i2cbus(c_char_p(self.__dev_name),c_int(self.__assign_addr))
		if(fd==1):
			raise IOError('Can\'t open I2C device driver')
		elif(fd==2):
			raise IOError('Can\'t assign device address')
		

################################################################################
#Функция вычесления контрольной суммы
################################################################################	

	def __calc_crc(self,crc,src,size):
		print "<i2c_bus.__calc_crc()"

		data=c_ubyte(0)
		crc=c_ushort(crc)
		for i in range(1,size):
			data.value=src[i]			
			data.value^=lo8(crc.value)
			data.value^=data.value<<4
			crc.value=((data.value<<8)|hi8(crc.value))^(data.value>>4)^(data.value<<3)
		print "/i2c_bus.__calc_crc()>"
		return crc.value	
		


################################################################################
# Функция заполнения self.__tx_buff буффера
################################################################################	

	def __fill_tx_packet(self,data,size):

		print "<i2c_bus.__fill_tx_packet()"									# Заполнение self.__tx_buff буффера
		self.size_tx_packet=size+5											#
		self.__tx_buff[0]=0x02												#
		self.__tx_buff[1]=(self.__count)&0x7f								#
		self.__tx_buff[2]=size												#
		for i in range(size):												#
			self.__tx_buff[3+i]=data[i]										#
	
		crc=self.__calc_crc(0xffff,self.__tx_buff,self.size_tx_packet-2)	# определение контрольной суммы пакета
		self.__tx_buff[self.size_tx_packet-2]=lo8(crc)						#
		self.__tx_buff[self.size_tx_packet-1]=hi8(crc)						#
	
		for i in range(self.size_tx_packet):								# Вывод self.__tx_buff буффера на экран
			print "FULL TX PACKET byte[",i,"]=",self.__tx_buff[i]			#
		print "/i2c_bus.__fill_tx_packet()>"								#
		
		
		
################################################################################
# Функция транзакции (если удачно возвращает ответ в виде list иначе возвращает 0)
################################################################################

	def transaction(self,data,size):
		print "<i2c_bus.transaction()"

		self.__fill_tx_packet(data,size)																							# заполнение пакета
		for i in range(3):

			if(not self.dl.write_to_i2cbus(self.__tx_buff,self.size_tx_packet)):													# отправка	self.__tx_buff буффера в шину I2C
				print  "i2c_bus.transaction()::Error sending the data packet."
				return -1 
				
			validator=self.__get_answ()																								# получение ответа

			if(not validator):																										#проверка ответного пакета
				print "i2c_bus.transaction()::error geting answer"
				print "i2c_bus.transaction()::setting a bit snooze and sending tx_packet again.Attempt sending ",1+i
				self.__tx_buff[1]=self.__tx_buff[1]|0x08
				crc=self.__calc_crc(0xffff,self.__tx_buff,self.size_tx_packet-2)
				self.__tx_buff[self.size_tx_packet-2]=lo8(crc)
				self.__tx_buff[self.size_tx_packet-1]=hi8(crc)
				continue

			else:
				print "i2c_bus.transaction()::Answer is valid."
				self.__count=self.__count+1
				print "/i2c_bus.transaction()>"
				return self.__rx_buff[3:-2]
		print "i2c_bus.transaction()>"
		return -1 
			
			
	
################################################################################
# Функция получения ответа
################################################################################	

	def __get_answ(self):
		self.__rx_buff=bytearray()																
		print "<i2c_bus.get_answ()"

		head_rx_packet=c_ubyte*3
		self.rx_head=head_rx_packet()

		self.bl_rx_data=c_ubyte*256
		self.bl_data=self.bl_rx_data()

		if(not self.dl.read_from_i2cbus(self.rx_head,3)):											# читаем первые 3 байта если неудача возвращаем 0						
			print "i2c_bus.__get_answ()::IO error.Can\'t read data from device"						#
			print "/i2c_bus.get_answ()>"															#
			return 0																				#
		
		if(self.rx_head[0]==0x05):																	# проверяем первый байт если nak или не stx возвращаем 0 
			print "i2c_bus.__get_answ()::NAK recieved."												#
			print "/i2c_bus.get_answ()>"															#
			return 0																				#	
		if(self.rx_head[0]!=0x02):																	#	
			print "i2c_bus.__get_answ()::Error getting answer. Wrong byte STX."						#
			print "/i2c_bus.get_answ()>"															#
			return 0																				#		


		if(not self.dl.read_from_i2cbus(self.bl_data,self.rx_head[2]+2 )):							# читаем остальные байты посылки если неудача возвращаем 0
			print "i2c_bus.__get_answ()::IO error"													#
			print "/i2c_bus.get_answ()>"															#
			return 0																				#
		self.__size_rx_packet=self.rx_head[2]+5														#		
		self.__rx_buff.append(self.rx_head[0])														#		
		self.__rx_buff.append(self.rx_head[1])														#	
		self.__rx_buff.append(self.rx_head[2])														#	
		for i in range(self.rx_head[2]+2):															#		
			self.__rx_buff.append(self.bl_data[i])	

		if(self.__calc_crc(0xffff,self.__rx_buff,self.__size_rx_packet)):							# проверка контрольной суммы
			print "i2c_bus.__get_answ()::Error: Invalid crc."										#
			print "/i2c_bus.get_answ()>"															#
			return 0																				#
			
		for i in range(len(self.__rx_buff)):														# выводим на экран принятую посылку
			print "FULL RX PACKET byte[",i,']',self.__rx_buff[i]									#
		print "/i2c_bus.get_answ()>"																#			
		return 1																					#	



################################################################################
# Функция запроса типа устройства
################################################################################	

	def get_device_type(self):
		print "<i2c_bus.get_device_type()"

		self.__full_tx_buff=[]
		self.__full_tx_buff.append(0x00)
		self.__full_rx_buff=self.transaction(self.__full_tx_buff,len(self.__full_tx_buff))
		if(self.__full_rx_buff==-1):
			print 'i2c_bus.get_device_type()::Transaction is failed'
			return -1
		print "/i2c_bus.get_device_type()>"
		return self.__full_rx_buff
		
		
		
################################################################################
# Функция запроса состояния буфера 
################################################################################	

	def get_state_buff(self,num_ch):
		print "<host.get_state_buff()"

		self.__full_tx_buff=[]
		self.__full_tx_buff.append(0x01)
		self.__full_tx_buff.append(num_ch)
		self.__full_rx_buff=self.transaction(self.__full_tx_buff,len(self.__full_tx_buff))
		if(self.__full_rx_buff==-1):
			print 'i2c_bus.get_state_buff()::Transaction is failed'
			return -1
		print "/host.get_state_buff()>"
		return self.__full_rx_buff
		
	
	
################################################################################
# Функция запроса на передачу
################################################################################	

	def transmit_req(self,num_ch,data,sizeData):
		print "<host.transmit_req()"
		self.__full_tx_buff=[]
		self.__full_tx_buff.append(0x02)
		self.__full_tx_buff.append(num_ch)
		for i in range(sizeData):
			if type(data[i]) is StringType:
				self.__full_tx_buff.append(ord(data[i]))
			else:	
				self.__full_tx_buff.append(data[i])
		
		for j in range(len(self.__full_tx_buff)):
			print 'TRANSMIT CMD byte[',j,']',self.__full_tx_buff[j]
		self._full_rx_buff=self.transaction(self.__full_tx_buff,len(self.__full_tx_buff))
		if(self.__full_rx_buff==-1):
			print 'i2c_bus.transmit_req()::Transaction is failed'
			return -1
		print "/host.transmit_req()>"
		return self.__full_rx_buff
		
		
		
################################################################################
# Функция запроса на прием
################################################################################	

	def receive_req(self,num_ch,clr_buff,size):
		print "<host.receive_req()"
		self.__full_tx_buff=[]
		self.__full_tx_buff.append(0x03)
		self.__full_tx_buff.append(num_ch)
		self.__full_tx_buff.append(clr_buff)
		self.__full_tx_buff.append(size)
		
		for j in range(len(self.__full_tx_buff)):
			print 'RECIEVE CMD byte[',j,']',self.__full_tx_buff[j]
		
		self.__full_rx_buff=self.transaction(self.__full_tx_buff,len(self.__full_tx_buff))
		if(self.__full_rx_buff==-1):
			print 'i2c_bus.receive_req()::Transaction is failed'
			return -1
		print "/host.receive_req()>"
		return self.__full_rx_buff



################################################################################
# Функция запроса получения параметров порта
################################################################################	

	def get_settings_port(self,num_ch):
		print "<host.get_settings_port()"

		self.__full_tx_buff=[]
		self.__full_tx_buff.append(0x04)
		self.__full_tx_buff.append(num_ch)
		self.__full_rx_buff=self.transaction(self.__full_tx_buff,len(self.__full_tx_buff))
		if(self.__full_rx_buff==-1):
			print 'i2c_bus.get_settings_port()::Transaction is failed'
			return -1
		print "/host.get_settings_port()>"
		return self.__full_rx_buff
		
		
		
################################################################################
# Функция запроса на установку параметров порта
################################################################################	
		
	def set_settings_port(self,num_ch,baudrate,bits):
		print "<host.set_settings_port()"

		self.__full_tx_buff=[]
		self.__full_tx_buff.append(0x05)
		self.__full_tx_buff.append(num_ch)
		self.__full_tx_buff.append(baudrate)
		self.__full_tx_buff.append(bits)
		self.__full_rx_buff=self.transaction(self.__full_tx_buff,len(self.__full_tx_buff))
		if(self.__full_rx_buff==-1):
			print 'i2c_bus.set_settings_port()::Transaction is failed'
			return -1
		print "/host.set_settings_port()>"
		return self.__full_rx_buff
		
		
		
################################################################################
# Функция запроса на действие с дисплеем
################################################################################	
		
	def config_display(self,delay_flag):
		print "<host.config_display()"

		self.__full_tx_buff=[]
		self.__full_tx_buff.append(0x06)
		self.__full_tx_buff.append(delay_flag)
		self.__full_rx_buff=self.transaction(self.__full_tx_buff,len(self.__full_tx_buff))
		if(self.__full_rx_buff==-1):
			print 'i2c_bus.config_display()::Transaction is failed'
			return -1
		print "/host.config_display()>"
		return self.__full_rx_buff
		
		
		
################################################################################
# Функция запроса на получение параметров нескольких портов
################################################################################	
	
	def get_state_buffers(self,type_buffs,count_buffs,fst_buff):
		print "<host.get_state_buffers()"

		self.__full_tx_buff=[]
		self.__full_tx_buff.append(0x07)
		self.__full_tx_buff.append((count_buffs|0x7f)|(type<<7))
		self.__full_rx_buff=self.transaction(self.__full_tx_buff,len(self.__full_tx_buff))
		if(self.__full_rx_buff==-1):
			print 'i2c_bus.get_state_buffers()::Transaction is failed'
			return -1	
		print "/host.get_state_buffers()>"
		return self.__full_rx_buff
		
		
		
################################################################################
# Функция закрытие дескриптора шины I2C
################################################################################
	def close(self):
		print "<i2c_bus.close()"
		
		if(self.dl.close_i2cbus()==-1):
			return -1
			print "/i2c_bus.close()>"
		print "/i2c_bus.close()>"
		return 0

#=============================================================================================================		
# end definition base class i2c_bus
#=============================================================================================================
