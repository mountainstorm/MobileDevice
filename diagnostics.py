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


class Diagnostics(PlistService):
	TYPE_ALL = u'All'
	TYPE_WIFI = u'WiFi'
	TYPE_GASGAUGE = u'GasGauge'
	TYPE_NAND = u'NAND'

	ACTION_WAIT_FOR_DISCONNECT = u'WaitForDisconnect'
	ACTION_DISPLAY_PASS = u'DisplayPass'
	ACTION_DISPLAY_FAIL = u'DisplayFail'

	def __init__(self, amdevice):
		PlistService.__init__(
			self,
			amdevice, 
			[AMSVC_MOBILE_DIAGNOSTICS_RELAY, AMSVC_IOSDIAGNOSTICS_RELAY],
			kCFPropertyListXMLFormat_v1_0
		)

	def disconnect(self):
		self.goodbye()
		PlistService.disconnect(self)

	def _action(self, name, actions):
		msg = {
			u'Request': name
		}
		for action in actions:
			msg[action] = True
		self._sendmsg(msg)
		return self._chkresult(self._recvmsg())

	def _chkresult(self, result):
		retval = False
		if result[u'Status'] == u'Success':
			retval = True
		return retval

	def goodbye(self):
		self._sendmsg({u'Request': u'Goodbye'})
		return self._chkresult(self._recvmsg())

	def sleep(self):
		self._sendmsg({u'Request': u'Sleep'})
		return self._chkresult(self._recvmsg())

	def restart(self, actions=[]):
		return self._action(u'Restart', actions)

	def shutdown(self, actions=[]):
		return self._action(u'Shutdown', actions)

	def diagnostics(self, typ):
		retval = None
		self._sendmsg({u'Request': typ})
		msg = self._recvmsg()
		if self._chkresult(msg):
			retval = msg[u'Diagnostics']
		return retval

	# look in com.apple.mobilegestalt.plist for values
	def mobilegestalt(self, keys):
		self._sendmsg({
			u'Request': u'MobileGestalt',
			u'MobileGestaltKeys': keys
		})
		msg = self._recvmsg()
		if self._chkresult(msg):
			retval = msg[u'Diagnostics']
		return retval

	# IODeviceTree, IOPower, IOService
	def ioregistry(self, plane=u'IOService', name=None, cls=None):
		msg = {
			u'Request': u'IORegistry',
			u'CurrentPlane': plane
		}
		if name is not None:
			msg[u'EntryName'] = name
		if cls is not None:
			msg[u'EntryClass'] = cls

		self._sendmsg(msg)
		msg = self._recvmsg()
		if self._chkresult(msg):
			retval = msg[u'Diagnostics']
		return retval


if __name__ == u'__main__':
	import pprint

	def factory(dev):
		d = AMDevice(dev)
		d.connect()
		diag = Diagnostics(d)
		print diag.diagnostics(Diagnostics.TYPE_GASGAUGE)
		print diag.diagnostics(Diagnostics.TYPE_WIFI)
		print diag.diagnostics(Diagnostics.TYPE_NAND)
		print diag.diagnostics(Diagnostics.TYPE_ALL)
		print
		print diag.mobilegestalt([u'UserAssignedDeviceName'])
		print
		pprint.pprint(diag.ioregistry())
		print
		diag.disconnect()
		return d
	
	handle_devices(factory)

