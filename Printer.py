#!/usr/bin/python
# -*- coding=utf-8 -*-

from types import *

class printer:
	def __init__(self,interface, numCh, baudrate):
		print '<Printer.__init__()'
		
		self.__iface=interface
		self.__baudrate=baudrate
		self.__numCh=numCh
		self.__configPrinter()
	
	def __configPrinter(self):
		print '<Printer.configPrinter()'
	
		if(self.__iface.set_settings_port(self.__numCh,self.__baudrate,8)<0):
			raise IOError('Printer.configPrinter()::Error : Can\'t set a settings for the printer\'s port')
			
	
	def printData(self,data):
		if(self.__iface.transmit_req(self.__numCh,data,len(data))<0):
			print '<Printer.print()::Error: Can\'t  transmit request'
			return -1
		return 1
		
	def lineFeed(self):
		if(self.__iface.transmit_req(self.__numCh,[0x0a],1)<0):
			print '<Printer.print()::Error: Can\'t  feed the line'
			return -1
		return 1
		
	def formFeed(self):
		if(self.__iface.transmit_req(self.__numCh,[0x0c],1)<0):
			print '<Printer.print()::Error: Can\'t  feed the line'
			return -1
		return 1