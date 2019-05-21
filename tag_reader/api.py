# -*- coding: utf-8 -*-

from . import register


class PN532(object):
	def __init__(self):
		# i2c device address
		self.address = register.PN532_DEFAULT_ADDRESS

	def setup(self):
		"""FIXME"""
		print("pn532 is setting up")

	def read(self):
		"""FIXME"""
		return 100
