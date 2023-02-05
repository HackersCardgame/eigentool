#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# A Person or Company or 

from model.Location import *

class Contact:

	def __init__(self):
		# class members
		
		self.title = None
		self.firstName = None
		self.lastName = None
		self.email = None
		self.email2 = None
		self.phone = None
		self.phone2 = None
		self.mobile = None
		
		self.address = Location()
