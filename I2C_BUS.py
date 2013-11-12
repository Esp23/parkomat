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

		self.__tx_buff=array_byte()																													# Tx буффер
		self.__rx_buff=array_byte()																													# Rx буффер
		self.__answer=bytearray()																													# Содержит ответ от устройства последней транзакции
		
		self.__lib_name=libName																														# Имя и полный путь к динамической библиотеке
		self.__assign_addr=assignAddr																												# Адресс устройства на шине I2C
		self.__dev_name=devName																														# Драйвер шины I2C
		self.__count=0																																# Счетчик посылок

		self.dl=cdll.LoadLibrary(self.__lib_name)																									# Загрузка динамической библиотеки
		
		fd=self.dl.open_i2cbus(c_char_p(self.__dev_name),c_int(self.__assign_addr))																	# Открываем драйвер шины I2C
		if(fd==1):																																	# Усли неудача формируем исключение 
			raise IOError('Can\'t open I2C device driver')																							# IOError
		elif(fd==2):																																#
			raise IOError('Can\'t assign device address')																							#
		

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

		print "<i2c_bus.__fill_tx_packet()"																											# Заполнение self.__tx_buff буффера
		self.size_tx_packet=size+5																													#
		self.__tx_buff[0]=0x02																														#
		self.__tx_buff[1]=(self.__count)&0x7f																										#
		self.__tx_buff[2]=size																														#
		for i in range(size):																														#
			self.__tx_buff[3+i]=data[i]																												#
	
		crc=self.__calc_crc(0xffff,self.__tx_buff,self.size_tx_packet-2)																			# определение контрольной суммы пакета
		self.__tx_buff[self.size_tx_packet-2]=lo8(crc)																								#
		self.__tx_buff[self.size_tx_packet-1]=hi8(crc)																								#
	
		for i in range(self.size_tx_packet):																										# Вывод self.__tx_buff буффера на экран
			print "FULL TX PACKET byte[",i,"]=",self.__tx_buff[i]																					#
		print "/i2c_bus.__fill_tx_packet()>"																										#
		
		
		
################################################################################
# Функция транзакции (если удачно возвращает ответ в виде list иначе возвращает 0)
################################################################################

	def transaction(self,data,size):
		print "<i2c_bus.transaction()"

		self.__fill_tx_packet(data,size)																											# заполнение пакета
		for i in range(3):

			if(not self.dl.write_to_i2cbus(self.__tx_buff,self.size_tx_packet)):																	# отправка	данных из self.__tx_buff буффера в шину I2C
				print  "i2c_bus.transaction()::Error sending the data packet."																		#
				return -1 																															#
				
			validator=self.__get_answ()																												# получение ответа от устройства на шине I2C(см. Протокол взаимодействия: Мост i2c-uart)

			if(validator):																															# Если прозошла ошибка при принятии ответа
				print "i2c_bus.transaction()::error geting answer"																					# Взводим бит повтора (см. Протокол взаимодействия: Мост i2c-uart)
				print "i2c_bus.transaction()::setting a bit snooze and sending tx_packet again.Attempt sending ",1+i								# и повторяем транзакцию (макс число повторений 3 раза после возвращаем -1)
				self.__tx_buff[1]=self.__tx_buff[1]|0x08																							#
				crc=self.__calc_crc(0xffff,self.__tx_buff,self.size_tx_packet-2)																	#
				self.__tx_buff[self.size_tx_packet-2]=lo8(crc)																						#
				self.__tx_buff[self.size_tx_packet-1]=hi8(crc)																						#
				continue

			else:																																	# Если ответ пришел коректно
				print "i2c_bus.transaction()::Answer is valid."																						# увиличиваем счетчик посылок
				self.__count=self.__count+1																											# и возвращаем 1
				print "/i2c_bus.transaction()>"																										#
				return 1																															#
		print "i2c_bus.transaction()>"																												#
		return -1 																																	#	
			
			
	
################################################################################
# Функция получения ответа
# Возвращаемые значения:
# 0-удачно
# 1-ошибка чтения байта
# 2-Получен NAK
# 3-Ошибка stx байта
# 4-Ошибка контрольной суммы
################################################################################	

	def __get_answ(self):
		self.__answer=bytearray()																													# Обнуляем RX буфер															
		print "<i2c_bus.get_answ()"																													#

		if(not self.dl.read_from_i2cbus(self.__rx_buff,3)):																							# читаем первые 3 байта если неудача возвращаем 						
			print "i2c_bus.__get_answ()::IO error.Can\'t read data from device"																		# код ошибки
			print "/i2c_bus.get_answ()>"																											#
			return 1																																#
		
		if(self.__rx_buff[0]==0x05):																												# проверяем первый байт если nak или не stx возвращаем 
			print "i2c_bus.__get_answ()::NAK recieved."																								# код ошибки
			print "/i2c_bus.get_answ()>"																											#
			return 2																																#	
		if(self.__rx_buff[0]!=0x02):																												#	
			print "i2c_bus.__get_answ()::Error getting answer. Wrong byte STX."																		#
			print "/i2c_bus.get_answ()>"																											#
			return 3																																#		
		
		self.__answer.append(self.__rx_buff[0])																										#
		self.__answer.append(self.__rx_buff[1])																										#
		self.__answer.append(self.__rx_buff[2])																										#
		
		if(not self.dl.read_from_i2cbus(self.__rx_buff,self.__answer[2]+2 )):																		# читаем остальные байты посылки если неудача возвращаем 
			print "i2c_bus.__get_answ()::IO error"																									# код ошибки
			print "/i2c_bus.get_answ()>"																											#
			return 1																																#

		for i in range(self.__answer[2]+2):																											#		
			self.__answer.append(self.__rx_buff[i])	

		if(self.__calc_crc(0xffff,self.__answer,self.__answer[2]+5)):																				# проверка контрольной суммы
			print "i2c_bus.__get_answ()::Error: Invalid crc."																						# если не верная возвращаем 
			print "/i2c_bus.get_answ()>"																											# код ошибки
			return 4																																#
			
		for i in range(len(self.__answer)):																											# выводим на экран принятую посылку
			print "FULL RX PACKET byte[",i,']',self.__answer[i]																						#
		print "/i2c_bus.get_answ()>"																												#			
		return 0																																	#	



################################################################################
# Функция запроса типа устройства
################################################################################	

	def get_device_type(self):
		print "<i2c_bus.get_device_type()"

		cmd=[]																																		# формируем данные команды
		cmd.append(0x00)																															#
		
		if(self.transaction(cmd,len(cmd))==-1):																										# передаем команду если транзакция не удалась
			print 'i2c_bus.get_device_type()::Transaction is failed'																				# возвращаем -1
			print "/i2c_bus.get_device_type()>"																										#
			return -1																																#
			
		if(self.__answer[3]!=0):																													# если удачно проверяем байт кода ошибки 
			print 'i2c_bus.get_device_type()::Error code-{}'.format(self.__answer[3])																		# если байт !=0 ошибка возвращаем -1 и выводим код ошибки на экран
			print "/i2c_bus.get_device_type()>"																										# и выводим код ошибки на экран
			return -2																																# (см. Протокол взаимодействия: Мост i2c-uart)
		
		print "/i2c_bus.get_device_type()>"																											# если 0 возвращаем ответ
		return self.__answer[3:-2]																													#
		
		
		
################################################################################
# Функция запроса состояния буфера 
#(см коментарии к get_device_type()-аналогично)
################################################################################	

	def get_state_buff(self,num_ch):
		print "<host.get_state_buff()"

		cmd=[]
		cmd.append(0x01)
		cmd.append(num_ch)
		
		if(self.transaction(cmd,len(cmd))==-1):
			print 'i2c_bus.get_state_buff()::Transaction is failed'
			print "/host.get_state_buff()>"
			return -1
		
		if(self.__answer[3]!=0):																													
			print 'i2c_bus.get_state_buff()::Error code-{}'.format(self.__answer[3])																		
			print "/i2c_bus.get_state_buff()>"																										
			return -2						
	
		print "/host.get_state_buff()>"
		return self.__answer[3:-2]
		
	
	
################################################################################
# Функция запроса на передачу
# (см коментарии к get_device_type()-аналогично)
################################################################################	

	def transmit_req(self,num_ch,data,sizeData):
		print "<host.transmit_req()"
		cmd=[]
		cmd.append(0x02)
		cmd.append(num_ch)
		for i in range(sizeData):
			if type(data[i]) is StringType:
				cmd.append(ord(data[i]))
			else:	
				cmd.append(data[i])
				
		if(self.transaction(cmd,len(cmd))==-1):
			print 'i2c_bus.transmit_req()::Transaction is failed'
			print "/host.transmit_req()>"
			return -1
		
		if(self.__answer[3]!=0):																													
			print 'i2c_bus.transmit_req()::Error code-{}'.format(self.__answer[3])																		
			print "/i2c_bus.transmit_req()>"																										
			return -2	
		
		print "/host.transmit_req()>"
		return self.__answer[3:-2]
		
		
		
################################################################################
# Функция запроса на прием	
# (см коментарии к get_device_type()-аналогично)
################################################################################	

	def receive_req(self,num_ch,clr_buff,size):
		print "<host.receive_req()"
		cmd=[]
		cmd.append(0x03)
		cmd.append(num_ch)
		cmd.append(clr_buff)
		cmd.append(size)
		
		if(self.transaction(cmd,len(cmd))==-1):
			print 'i2c_bus.receive_req()::Transaction is failed'
			print "/host.receive_req()>"
			return -1
			
		if(self.__answer[3]!=0):																													
			print 'i2c_bus.receive_req()::Error code-{}'.format(self.__answer[3])																		
			print "/i2c_bus.receive_req()>"																										
			return -2	
		
		print "/host.receive_req()>"
		return self.__answer[3:-2]



################################################################################
# Функция запроса получения параметров порта
# (см коментарии к get_device_type()-аналогично)
################################################################################	

	def get_settings_port(self,num_ch):
		print "<host.get_settings_port()"

		cmd=[]
		cmd.append(0x04)
		cmd.append(num_ch)
		if(self.transaction(cmd,len(cmd))==-1):
			print 'i2c_bus.get_settings_port()::Transaction is failed'
			print "/host.get_settings_port()>"
			return -1
			
		if(self.__answer[3]!=0):																													
			print 'i2c_bus.get_settings_port()::Error code-{}'.format(self.__answer[3])																		
			print "/i2c_bus.get_settings_port()>"																										
			return -2	
		
		print "/host.get_settings_port()>"
		return self.__answer[3:-2]
		
		
		
################################################################################
# Функция запроса на установку параметров порта
# (см коментарии к get_device_type()-аналогично)
################################################################################	
		
	def set_settings_port(self,num_ch,baudrate,bits):
		print "<host.set_settings_port()"

		cmd=[]
		cmd.append(0x05)
		cmd.append(num_ch)
		cmd.append(baudrate)
		cmd.append(bits)
		
		if(self.transaction(cmd,len(cmd))==-1):
			print 'i2c_bus.set_settings_port()::Transaction is failed'
			print "/host.set_settings_port()>"
			return -1
		
		if(self.__answer[3]!=0):																													
			print 'i2c_bus.set_settings_port()::Error code-{}'.format(self.__answer[3])																		
			print "/i2c_bus.set_settings_port()>"																										
			return -2	
		
		print "/host.set_settings_port()>"
		return self.__answer[3:-2]
		
		
		
################################################################################
# Функция запроса на действие с дисплеем
#(см коментарии к get_device_type()-аналогично)
################################################################################	
		
	def config_display(self,delay_flag):
		print "<host.config_display()"

		cmd=[]
		cmd.append(0x06)
		cmd.append(delay_flag)
		
		if(self.transaction(cmd,len(cmd))==-1):
			print 'i2c_bus.config_display()::Transaction is failed'
			print "/host.config_display()>"
			return -1
			
		if(self.__answer[3]!=0):																													
			print 'i2c_bus.config_display()::Error code-{}'.format(self.__answer[3])																		
			print "/i2c_bus.config_display()>"																										
			return -2	
			
		print "/host.config_display()>"
		return self.__answer[3:-2]
		
		
		
################################################################################
# Функция запроса на получение параметров нескольких портов
# (см коментарии к get_device_type()-аналогично)
################################################################################	
	
	def get_state_buffers(self,type_buffs,count_buffs,fst_buff):
		print "<host.get_state_buffers()"

		cmd=[]
		cmd.append(0x07)
		cmd.append((count_buffs|0x7f)|(type<<7))
		
		if(self.transaction(cmd,len(cmd))==-1):
			print 'i2c_bus.get_state_buffers()::Transaction is failed'
			print "/host.get_state_buffers()>"
			return -1	
			
		if(self.__answer[3]!=0):																													
			print 'i2c_bus.get_state_buffers()::Error code-{}'.format(self.__answer[3])																		
			print "/i2c_bus.get_state_buffers()>"																										
			return -2	
			
		print "/host.get_state_buffers()>"
		return self.__answer[3:-2]
		
		
		
################################################################################
# Функция закрытие дескриптора шины I2C
# (см коментарии к get_device_type()-аналогично)
################################################################################
	def close(self):
		print "<i2c_bus.close()"
		
		if(self.dl.close_i2cbus()==-1):
			print "/i2c_bus.close()>"
			return -1
			print "/i2c_bus.close()>"
		print "/i2c_bus.close()>"
		return 0

#=============================================================================================================		
# end definition base class i2c_bus
#=============================================================================================================
