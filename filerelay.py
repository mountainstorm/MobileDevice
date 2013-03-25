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
from amdevice import *
from plistservice import *
import os


class FileRelay(PlistService):
	def __init__(self, amdevice):
		PlistService.__init__(
			self,
			amdevice, 
			[AMSVC_FILE_RELAY],
			kCFPropertyListXMLFormat_v1_0
		)

	# AppleSupport
	# Network
	# VPN
	# WiFi
	# UserDatabases
	# CrashReporter
	# tmp
	# SystemConfiguration
	# returns a .cpio.gz file with the contents
	def request(self, sources):
		retval = False
		self._sendmsg({u'Sources': sources})
		reply = self._recvmsg()
		if u'Status' in reply and reply[u'Status'] == u'Acknowledged':
			# now read the cpio.gz file it returns
			retval = ''
			while True:
				data = os.read(fr.s, 1024)
				if data is None or len(data) == 0:
					break
				retval += data
		return retval


if __name__ == u'__main__':
	def factory(dev):
		d = AMDevice(dev)
		d.connect()
		fr = FileRelay(d)

		f = open(u'dump.cpio.gz', 'wb')
		f.write(fr.retrieve([
			u'AppleSupport',
			u'Network',
			u'VPN',
			u'WiFi',
			u'UserDatabases',
			u'CrashReporter',
			u'tmp',
			u'SystemConfiguration'
		]))
		f.close()

		fr.disconnect()
		return d
	
	handle_devices(factory)

