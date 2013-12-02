#!/usr/bin/python
# -*- coding: utf-8 -*-
from I2C_BUS import *
from BillValidator import *
from Printer import *
from PIL import Image
import qrcode 


#===================================================================================================
# Таблица приведения кодировки koi8-r к кодировке Pc437
#===================================================================================================
KOI8_R_to_PC865=[
0xC4,0xb3,0xDA,0xBF,0xc0,0xd9,0xc3,0xb4,0xc2,0xc1,0xc5,0xdf,0xdc,0xdb,0xdd,0xde,
0xb0,0xb1,0xb2,0xf4,0xff,0xf9,0xfb,0xf7,0xf3,0xf2,0xff,0xf5,0xf8,0xfd,0xfa,0xf6,
0xcd,0xba,0xd5,0xf1,0xd6,0xc9,0xb8,0xb7,0xbb,0xd4,0xd3,0xc8,0xbe,0xbd,0xbc,0xc6,
0xc7,0xcc,0xb5,0xf0,0xb6,0xb9,0xd1,0xd2,0xcb,0xcf,0xd0,0xca,0xd8,0xd7,0xce,0xff,
0xee,0xa0,0xa1,0xe6,0xa4,0xa5,0xe4,0xa3,0xe5,0xa8,0xa9,0xaa,0xab,0xac,0xad,0xae,
0xaf,0xef,0xe0,0xe1,0xe2,0xe3,0xa6,0xa2,0xec,0xeb,0xa7,0xe8,0xed,0xe9,0xe7,0xea,
0x9e,0x80,0x81,0x96,0x84,0x85,0x94,0x83,0x95,0x88,0x89,0x8a,0x8b,0x8c,0x8d,0x8e,
0x8f,0x9f,0x90,0x91,0x92,0x93,0x86,0x82,0x9c,0x9b,0x87,0x98,0x9d,0x99,0x97,0x9a
]

##############################################################################################################
# Класс исключения 
##############################################################################################################

class parkomatError(Exception):
	
	def __init__(self,value):
		self.value=value
	def __str__(self):
		return repr(self.value)
		
		

##############################################################################################################
# Класс паркомат
##############################################################################################################
class parkomat:
	
	def __init__(self,configFile):
	
		self.__config_File=configFile																	# Переменная содержащая путь и имя файла конфигурации
		self.__tx_buff=[]																				# tx Буффер
		self.__ticket=[]																				# Массив содержащий данные чека 
		self.__img_data=[]																				# Массив содержащий данные qr кода
		self.__ticket_File=""																			# Переменная содержащая путь и имя файла чека	
		self.__hourly_rate=0																			# Переменная храняшая стоимость одного часа стоянки
		self.__period=0																					# Переменная хранящая количество оплаченных часов
		self.__cash=0																					# Переменная содержащяя внесенную сумму последнего сеанса
		self.__max_sum=0																				# Максимальная сумма принимаемая паркоматом
		self.__qr=0																						# Переменная для хранения экземпляра класса QRcode
		self.ticketID=0																					# Id чека
		self.numTerm=''																					# Номер терминала
		
		self.__host=0																					# Переменная для хранения экземпляра класса шины I2C
		self.__libName=""																				# Переменная содержащая путь к библиотеке libi2c.so
		self.__devName=""																				# Переменная содержащая имя драйвера шины I2C
		self.__assignAddr=0																				# Переменная содержащая адрес устройства на шине I2C

		self.__billvalidator=0																			# Переменная для хранения экземпляра класса купюроприемника
		self.__numChBillValid=0																			# Номер канала купюроприемника	
		self.__spdBillValid=0																			# Скорость передачи данных по последвоательному порту купюроприемника

		self.__printer=0																				# Переменная для хранения экземпляра класса принтера
		self.__numChPrinter=0																			# Номер канала принтера
		self.__spdPrinter=0																				# Скорость передачи данных по последвоательному порту принтера
		
		self.__config_system()																			# функция настройки системы				
		
		
		


##############################################################################################################
# Функция конфигурирования системы
##############################################################################################################

	def __config_system(self):
		print "parkomat.__config_system()"		
		
		fd=open(self.__config_File,"r")																	# Открытие файла конфигурации системы
		for line in fd:																					# Читаем построчно файл конфигурации
			if(line[0]=='#'):
				continue
			
			if(line.find("ticket file")!=-1):															# Если содержит строку 'ticket_file' извлекаем данные пути и имени файла чека
				start=line.find("-")+1																	#
				end=line.find(";",start)																#
				self.__ticket_File=line[start:end].strip()												#
				print 'полный путь до файла чека',self.__ticket_File									#

			if(line.find("hourly rate")!=-1):															# Если содержит строку 'hourly_rate' извлекаем данные стоимости одного часа стоянки
				start=line.find("-")+1																	#
				end=line.find(";",start)																#														
				self.__hourly_rate=int(line[start:end].strip())										    #					
				print 'стоимость стоянки в час',self.__hourly_rate										#
				
			if(line.find("max sum")!=-1):																# Если содержит строку 'max sum' извлекаем максимальное значения принимаемой суммы за сеанс
				start=line.find("-")+1																	#
				end=line.find(";",start)																#
				self.__max_sum=int(line[start:end].strip())												#
				print "максимальная принимаемая сумма",self.__max_sum									#
				
			if(line.find("numTerm")!=-1):																# Если содержит строку 'numTerm' извлекаем строку номера терминала
				start=line.find("-")+1																	#
				end=line.find(";",start)																#
				self.numTernm=line[start:end].strip()													#
				print "Номер терминала",self.numTerm													#	
			
			if(line.find("library")!=-1):																# Если содержит строку 'library' извлекаем данные пути и имени библиотеки шины I2C
				start=line.find("-")+1																	#
				end=line.find(";",start)																#
				self.__libName=line[start:end].strip()													#
				print "полный путь до библиотеки:",self.__libName										#
		
			if(line.find("device")!=-1):																# Если содержит строку 'device' извлекаем имя драйвера устройства I2C
				start=line.find("-")+1																	#
				end=line.find(";",start)																#
				self.__devName=line[start:end].strip()													#
				print 'имя устройства',self.__devName													#

			if(line.find("address")!=-1):																# Если содержит строку 'address' извлекаем адрес устройства I2C
				start=line.find("-")+1																	#
				end=line.find(";",start)																#
				self.__assignAddr=int(line[start:end].strip())											#
				print 'адрес устройства I2C',self.__assignAddr											#

			if(line.find("bill validator channel")!=-1):												# Если содержит строку 'bill validator channel' извлекаем номер канала купюроприемника
				start=line.find("-")+1																	#
				end=line.find(";",start)																#
				self.__numChBillValid=int(line[start:end].strip())										#
				print "номер канала купюроприемника",self.__numChBillValid								#	
				
			if(line.find("billValidatorSpeed")!=-1):													# Если содержит строку 'billValidatorSpeed' извлекаем  значение скорости порта купюроприемника
				start=line.find("-")+1																	#
				end=line.find(";",start)																#
				self.__spdBillValid=int(line[start:end].strip())										#
				print "Скорость порта купюроприемника",self.__spdBillValid								#
				
			if(line.find("printer channel")!=-1):														# Если содержит строку 'printer channel' извлекаем номер канала принтера
				start=line.find("-")+1																	#
				end=line.find(";",start)																#
				self.__numChPrinter=int(line[start:end].strip())										#
				print "номер канала принтера",	self.__numChPrinter										#
				
			if(line.find("printerSpeed")!=-1):															# Если содержит строку 'printerSpeed' извлекаем  значение скорости порта принтера
				start=line.find("-")+1																	#
				end=line.find(";",start)																#
				self.__spdPrinter=int(line[start:end].strip())											#
				print "Скорость порта принтера",self.__spdPrinter										#
				

		self.__host=i2c_bus(self.__libName,self.__devName,self.__assignAddr)										# Создаем экземпляр класса I2C_BUS.py
			
		self.__billvalidator=bill_validator(self.__host,3,self.__numChBillValid,self.__spdBillValid,self.__max_sum)	# Создаем экземпляр класса BillValidator() купюроприемника
		if(self.__billvalidator.reset()<0):																			# И подаем команду reset
			raise parkomatError('Can\'t reset a bill validator.')
			
		self.__printer=printer(self.__host,self.__numChPrinter,self.__spdPrinter)									# Создаем экземпляр класса Printer() принтера
				
		if(self.__host.transmit_req(6,[0x12,0x02],2)==-1):															# Установка кодировки дисплея см. протокол взаимодействия i2c-uart
			raise parkomatError("parkomat.__config_system()::Error: can\'t set printer's character table")			# если не удачно формируем исключение ParkomatError 


##############################################################################################################
# Функция формирования данныч чека
##############################################################################################################

	def __createTicket(self):
		print "parkomat.createTicket(self)"																

		self.__ticket=[]																				# обнуление массива хранящего данные чека
		self.ticketID=self.ticketID+1
		self.__qr=qrcode.QRCode(																		# создаем класс экземпляр класса QRcode для создания qr кода											
			version=None,																				# поле отвечает за максимальный размер qr кода
			error_correction=qrcode.constants.ERROR_CORRECT_L,											# поле отвечает за обработку ошибок
			box_size=1,																					# определяет количество пикселей в одном квадрате
			border=0,																					# ширина рамки в квадратах
		)	
		
		fd=open(self.__ticket_File,"r")																	# Открываем файл чека
		for line in fd:																					# читаем построчно данные чека
			line=line.rstrip('\n')																		# удаляем символы переноса строки из всех строчек
			
			if(line.find("Налич")!=-1):																	# если строка содержит строку "Налич" 
				line=line.format(str(self.__cash))														# добавляем в конец строки данные внесенных наличных
				self.__qr.add_data(line)																# и кодируем строку в qrcode
				
			if(line.find("Опл. в ч")!=-1):																# если строка содержит строку "Опл. в ч" 
				line=line.format(str(self.__hourly_rate))												# добавляем в конец строки данные стоимости услуги в час
				self.__qr.add_data(line)																# и кодируем строку в qrcode
				
			self.__period=(self.__cash/self.__hourly_rate)												# расчет времени по внесенной сумме
			if(line.find("Кол. часов")!=-1):															# если строка содержит строку "Кол. часов" 
				line=line.format(str(self.__period))													# добавляем в конец строки данные времени по внесенной сумме
				self.__qr.add_data(line)																# и кодируем строку в qrcode
			
			if(line.find("Номер чека")!=-1):															# если строка содержит строку "Номер чека" 
				strTicketId=''																			# преобразуем данные номера чека  к шестисимвольной строке 																
				for i in range(6-len(str(self.ticketID))):												# и добавляем данные в конец строки 
					strTicketId=strTicketId+'0'															# и кодируем строку в qrcode
				strTicketId=strTicketId+str(self.ticketID)												#
				line=line.format(strTicketId)															# 
				self.__qr.add_data(line)																# 
			
			
			line=line.decode('utf-8')																	# преобразование строки из кодировки utf-8
			line=line.encode('koi8-r')																	# в кодировку koi8-r и добавление в масив данных чека 
			
			strData=[]																					# буфер для хранения данных перекодированной строки(PC437)/обнуление 																				
			for ch in line:																				# читаем строку посимвольно
				if(ord(ch)<0x80):																		# если байт < 0x80 добавляем в буффер strData
					strData.append(ord(ch))																# иначе преобразуем к таблице кодировки PC437 [U.S.A.,Standart Europe]
				else:																					#
					strData.append(KOI8_R_to_PC865[ord(ch)-0x80])										#
			self.__ticket.append(strData)																# 

		fd.close()																						# закрываем фаил чека
		
		self.__qr.make(fit=True)																		# сохраняем qrcode в виде изображения в формате .png
		img=self.__qr.make_image()																		# и вызываем функцию по преобразованию картинки qr кода в масив символов
		img.save('qrcode.png')																			#
		self.__conversionQrcode()																		#
	
	
	
	
##############################################################################################################
# Функция преобразования изображения qrcode.png в массив данных
##############################################################################################################
	
	def __conversionQrcode(self):
		self.__img_data=[]																				# обнуление массива хранящего данные qr кода
		
		img=Image.open('qrcode.png')																	# открываем изображение с qr кодом
		pix_val=list(img.getdata())																		# считываем данные пикселей изображения
		size=img.size																					# получение размера изображения в пикселях
		width=size[0]																					#
		heigh=size[1]																					#
	
		if(heigh%2):																					# проверяем высоту изображения если нечетная 
			for k in range(width):																		# добавляем в массив pix_val один ряд из
				pix_val.append(255)																		# белых пикселей (это делается так как анализ идет по 2 м строкам пикселей)
			heigh=heigh+1																				#
	
		for i in range(0,heigh,2):																		# Анализируем массив с данными пикселей изображения
			img_row=[]																					# создаем массив который хранит данные 2х строк пикселей
			
			for j in range(width):																		#
				index=i*(width)+j																		# вычисляем индекс данных пикселя массива pix_val[]
				if(pix_val[index]==pix_val[index+width]==255):											# и анализируем пиксель и пиксель след строки с тем же смещением
					img_row.append(0x20)																# если = между собой и = 255 добавляем в массив img_row[] символ 0x20(таблица кодировки PC437 [U.S.A.,Standart Europe])
				if(pix_val[index]==pix_val[index+width]==0):											# если = между собой и = 0 добавляем в массив img_row[] символ 0xDB(таблица кодировки PC437 [U.S.A.,Standart Europe])
					img_row.append(0xDB)																# если 1й пиксель > 2го соответственно добавляем в массив img_row[] символ 0xDС(таблица кодировки PC437 [U.S.A.,Standart Europe])
				if(pix_val[index]>pix_val[index+width]):												# если 1й пиксель < 2го соответственно добавляем в массив img_row[] символ 0xDF(таблица кодировки PC437 [U.S.A.,Standart Europe])
					img_row.append(0xDC)																#
				if(pix_val[index]<pix_val[index+width]):												#
					img_row.append(0xDF)																#
					
			self.__img_data.append(img_row)																# Добавляем массив img_row[] в массив self.__img_data[]
			
			
##############################################################################################################
# Функция печати чека
##############################################################################################################		
			
	def print_ticket(self):	
		print "parkomat.print_ticket()"

		self.__createTicket()																			# вызов функции формирования данных чека
		for i in self.__ticket:																			# читаем данные из массива с данными чека построчно
	
			if(self.__printer.printData(i)<0):															# передаем данные tx буффера в канал принтера
				print "parkomat.print_ticket()::Error:	Can\'t print the data ticket"					# если ошибка возвращаем 0
				return -1																				#
			if(self.__printer.lineFeed()<0):															# перенос строки принтера см. протокол взаимодействия i2c-uart и руководство пользователя принтера VKP80
				print "parkomat.print_ticket()::Error: Can\'t  feed the line"							#
				return -1


		for j in self.__img_data:																		# читаем и передаем данные qr кода в канал принтера
			if(self.__printer.printData(j)<0):															# если ошибка возвращаем 0
				print "parkomat.print_ticket()::Error: Can\'t print the QRCODE"							#
				return -1																				#
			if(self.__printer.lineFeed()<0):															# перенос строки принтера см. протокол взаимодействия i2c-uart и руководство пользователя принтера VKP80
				print "parkomat.print_ticket()::Error: Can\'t  feed the line"							#
				return -1	
				
		if(self.__printer.formFeed() < 0):																# обрезка и предоставление чека см. протокол взаимодействия i2c-uart и руководство пользователя принтера VKP80
				print "parkomat.print_ticket()::Error: Can\'t  feed the form"							#
				return -1	
		return 1																						# если все нормально возвращаем 1




##############################################################################################################
# Функция приема наличных
##############################################################################################################					
				
	def receiving_bills(self):
		self.__host.receive_req(6,2,0)																	# Очищаем буффер приемника канала купюроприемника
		self.__cash=0																					#
		status=0																						# переменная состояния купюроприемника
		while(1):																						# и запускаем пулинг купюроприемника
		
			time.sleep(0.2)																				# задержка в 200 мс
			status=	self.__billvalidator.Poll()															#
			if(status==-1):																				#
				print 'parkomat.receiving_bills()::Error: CRC is not valid'
				self.__billvalidator.sendNAK()
				continue
			if(status==-2):																				#
				raise  parkomatError('parkomat.receiving_bills()::Error: Poll command is failed')
			
			self.__billvalidator.sendACK()

			if(status==self.__billvalidator.states.Unit_Disabled):										# проверяем статус если disabled даем команду enabled
				self.__billvalidator.enable(0xff,0xff,0xff,0xff,0xff,0xff)								#
				
			if(status==self.__billvalidator.states.Idling):												# проверяем статус если Idling 
				fl=self.__host.receive_req(6,1,1)														# проверяем не была ли нажата кнопка оплатить
				if(fl>0):																				#
					if(fl[0]==0 and fl[3]==ord('D')):													# если была нажата отключаем прием купюр
																										#	
						if(self.__billvalidator.disable()<0):											# 
							raise parkomatError('Error disable the bill validator')						#
						
						res=self.__billvalidator.Poll()													#
						
						if(res==-1):																	# и возвращаем принятую сумму
							self.__billvalidator.sendNAK()												#
							self.__billvalidator.cursum=0												#
							return self.__cash															#
						
						if(res==-2):																	#
							raise parkomatError('Poll command is failed')								#		
						
						self.__billvalidator.sendACK()													#
						self.__billvalidator.cursum=0													#
						return self.__cash	
						
			if(self.__cash!=self.__billvalidator.cursum):												#
				self.__cash=self.__billvalidator.cursum													#
				self.display('Внесенно-{}р.'.format(self.__cash))										#
				
				
				
##############################################################################################################
# Функция возвращает стоимость услуги в час
##############################################################################################################		

	def get_hourly_rate(self):
		return self.__hourly_rate


##############################################################################################################
# Функция возвращает сумму внесенных наличных последнего сеанса
##############################################################################################################		
	def get_cash(self):
		return self.__cash


##############################################################################################################
# Функция отображения сообщения на дисплей паркомата
##############################################################################################################		

	def display(self,message):
		message=message.decode('utf-8')
		message=message.encode('koi8-r')
		self.__host.transmit_req(6,[0x10],1)
		self.__host.transmit_req(6,message,len(message))


##############################################################################################################
# конец обьявления класса Parkomat
##############################################################################################################		
		
example=parkomat("./config/config.cfg")
#while(1):
	#example.display('Cтоим.усл.-{}р/ч'.format(example.get_hourly_rate()))
	#if(not example.receiving_bills()):
	#	example.display('Внесите налич.\nи нажмите\nклавишу\'ввод\'')
	#	time.sleep(3)
	#	continue
print example.numTerm
example.print_ticket()
