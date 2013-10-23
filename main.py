#!/usr/bin/python
# -*- coding: utf-8 -*-
from I2C_BUS import *
from BillValidator import *
from PIL import Image
import qrcode 


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

#===================================================================================================

class parkomat:
	
	def __init__(self,configFile):
		self.__billvalidator=0
		self.__tx_buff=[]
		self.__host=0
		self.__qr=0
		self.__libName=""
		self.__devName=""
		self.__assignAddr=0
		self.__config_File=configFile
		self.__ticket=[]
		self.__ticket_File=""
		self.__cash=200
		self.__hourly_rate=0
		self.__period=2
		self.__config_system()

#===================================================================================================

	def __config_system(self):
		print "parkomat.__config_system()"		
		
		fd=open(self.__config_File,"r")
		for line in fd:
			if(line.find("hourly rate")!=-1):
				start=line.find("-")+1
				end=line.find(" ",start)
				self.__hourly_rate=int(line[start:end])	
				print self.__hourly_rate
			
			if(line.find("ticket file")!=-1):
				start=line.find("-")+1
				end=line.find(" ",start)
				self.__ticket_File=line[start:end]	
				print self.__ticket_File
				
			if(line.find("library")!=-1):
				start=line.find("-")+1
				end=line.find(" ",start)
				self.__libName=line[start:end]
				print self.__libName
		
			if(line.find("address")!=-1):
				start=line.find("-")+1
				end=line.find(" ",start)
				self.__assignAddr=int(line[start:end])
				print self.__assignAddr
				
			if(line.find("device")!=-1):
				start=line.find("-")+1
				end=line.find(" ",start)
				self.__devName=line[start:end]
				print self.__devName
		
		self.__host=i2c_bus("./config/lib/libi2c.so","/dev/i2c-1",4)
		
		self.__billvalidator=bill_validator(self.__host,3,3)
		
		self.__qr=qrcode.QRCode(
			version=None,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=1,
			border=0,
		)

#===================================================================================================

	def __createTicket(self):
		print "parkomat.createTicket(self)"

		fd=open(self.__ticket_File,"r")
		for line in fd:
			self.__ticket.append(line)
			
		for i in range(len(self.__ticket)):
			if(self.__ticket[i].find("Налич")!=-1):
				self.__ticket[i]=self.__ticket[i].rstrip('\n ')+str(self.__cash)+".00\n"
				self.__qr.add_data(self.__ticket[i])
			if(self.__ticket[i].find("Опл. в ч")!=-1):
				self.__ticket[i]=self.__ticket[i].strip('\n ')+str(self.__hourly_rate)+".00\n"
				self.__qr.add_data(self.__ticket[i])
			if(self.__ticket[i].find("Кол. часов")!=-1):
				self.__ticket[i]=self.__ticket[i].strip('\n ')+str(self.__period)+".00\n"
				self.__qr.add_data(self.__ticket[i])
			if(self.__ticket[i].find("Сдача")!=-1):
				self.__ticket[i]=self.__ticket[i].strip('\n ')+str(self.__cash-(self.__period*self.__hourly_rate))+".00\n"
				#self.__qr.add_data(self.__ticket[i])
		
		for i in range(len(self.__ticket)):
			line=self.__ticket[i]
			line=line.decode('utf-8')
			line=line.encode('koi8-r')
			self.__ticket[i]=line
		
		self.__qr.make(fit=True)
		img=self.__qr.make_image()
		img.save('qrcode.png')
		self.__conversionQrcode()
	
#===================================================================================================
	
	def __conversionQrcode(self):
		self.__img_data=[]
		self.__img_row=[]
		offset=0
		img=Image.open('qrcode.png')
		pix_val=list(img.getdata())
		print pix_val
		size=img.size
		width=size[0]
		heigh=size[1]
	
		if(heigh%2):
			for k in range(width):
				pix_val.append(255)
			heigh=heigh+1
	
		for i in range(0,heigh,2):
			self.__img_row=[]
			for j in range(width):
				index=i*(width)+j
				print pix_val[index],pix_val[index+width]
				
				if(pix_val[index]==pix_val[index+width]==255):
					self.__img_row.append(0x20)
				if(pix_val[index]==pix_val[index+width]==0):
					self.__img_row.append(0xDB)
				if(pix_val[index]>pix_val[index+width]):
					self.__img_row.append(0xDC)
				if(pix_val[index]<pix_val[index+width]):
					self.__img_row.append(0xDF)
			print self.__img_row
			#self.__img_row.append(ord('\n'))
			self.__img_data.append(self.__img_row)
			
			
#===================================================================================================		
			
	def print_ticket(self):	
		print "parkomat.print_ticket()"

		self.__createTicket()
		if(not self.__host.set_settings_port(1,16,8)):
			print "parkomat.print_ticket()::error set settings port"
		self.__host.transmit_req(2,[0x1b,0x4d,0x00],3)	
				
		for i in self.__ticket:
			self.__tx_buff=[]
			print "parkomat.print_ticket()::",i
			
			for j in i:
				if(ord(j)<0x80):
					self.__tx_buff.append(ord(j))
				else:
					self.__tx_buff.append(KOI8_R_to_PC865[ord(j)-0x80])
			if(not self.__host.transmit_req(2,self.__tx_buff,len(self.__tx_buff))):
				print "parkomat.print_ticket()::error transmit request."
				return 0
				
		
		
		for k in range(len(self.__img_data)):
			print "\n",self.__img_data[k]
			if(not self.__host.transmit_req(2,self.__img_data[k],len(self.__img_data[k]))):
				print "parkomat.print_ticket()::error transmit request."
				return 0
			self.__host.transmit_req(2,[0x0a],1)
		self.__host.transmit_req(2,[0x0c],1)
		return 1
	#def print_ticket(self,cash,time):
				
#----------------------------------------------------------------------------------------------------
		
example=parkomat("./config/config.cfg")
example.print_ticket()
