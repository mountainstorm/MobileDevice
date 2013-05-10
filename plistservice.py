#!/usr/bin/python
# coding: utf-8

# Copyright (c) 2013 Mountainstorm
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from MobileDevice import *
import os
import struct


class PlistService(object):
	def __init__(self, amdevice, servicenames, format=kCFPropertyListBinaryFormat_v1_0):
		self.format = format
		self.s = None
		self.dev = amdevice
		self.format = format
		for name in servicenames:
			self.s = amdevice.start_service(name)
			if self.s is not None:
				break

		if self.s is None:
			raise RuntimeError(u'Unable to launch one of:', servicenames)

	def disconnect(self):
		os.close(self.s)

	def _sendmsg(self, msg):
		data = dict_to_plist_encoding(msg, self.format)
		os.write(self.s, struct.pack(u'>I'.encode(u'utf-8'), len(data)))
		os.write(self.s, data)


	def _recvmsg(self):
		l = struct.unpack(u'>I'.encode(u'utf-8'), os.read(self.s, 4))[0]
		reply = ''
		left = l
		while left > 0:
			r = os.read(self.s, left) 
			if r is None:
				raise RuntimeError(u'Unable to read reply')
			reply += r
			left -= len(r)
		return dict_from_plist_encoding(reply, self.format)





