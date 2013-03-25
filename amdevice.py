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


class AMDevice(object):
	def __init__(self, dev):
		self.dev = dev
		self.deviceid = CFTypeTo(AMDeviceCopyDeviceIdentifier(self.dev))

	def connect(self):
		if AMDeviceConnect(self.dev) != MDERR_OK: 
			raise RuntimeError(u'Unable to connect to device')

		if AMDeviceIsPaired(self.dev) != 1:
			raise RuntimeError(u'if your phone is locked with a passcode, unlock then reconnect it')

		if AMDeviceValidatePairing(self.dev) != MDERR_OK: 
			raise RuntimeError(u'Unable to validate pairing')

		if AMDeviceStartSession(self.dev) != MDERR_OK: 
			raise RuntimeError(u'Unable to start session')

	def disconnect(self):
		AMDeviceStopSession(self.dev)
		AMDeviceRelease(self.dev)

	def start_service(self, service_name):
		sock = c_int()
		if AMDeviceStartService(self.dev, service_name, byref(sock)) != MDERR_OK:
			raise RuntimeError(u'Unable to start service %s' % service_name)
		return sock.value

	def copy_value(self, domain=None, value_name=None):
		retval = None
		d = CFTypeFrom(domain)
		v = CFTypeFrom(value_name)
		value = AMDeviceCopyValue(self.dev, d, v)
		if d is not None: 
			CFRelease(d)
		if v is not None:
			CFRelease(v)
		if value is None:
			raise RuntimeError(u'Unable to copy value %s/%s' % (domain, value_name))

		if value is not None:
			retval = CFTypeTo(value)
			CFRelease(value)
		return retval


def handle_devices(factory):
	devices = {}

	def cbFunc(info, cookie):
		info = info.contents
		if info.message == ADNCI_MSG_CONNECTED:
			devices[info.device] = factory(info.device)

		elif info.message == ADNCI_MSG_DISCONNECTED:
			devices[info.device].disconnect()
			del devices[info.device]			

	notify = AMDeviceNotificationRef()
	notifyFunc = AMDeviceNotificationCallback(cbFunc)
	err = AMDeviceNotificationSubscribe(notifyFunc, 0, 0, 0, byref(notify))
	if err != MDERR_OK:
		raise RuntimeError(u'Unable to subscribe for notifications')

	while CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.1, False) == kCFRunLoopRunTimedOut:
		pass

	AMDeviceNotificationUnsubscribe(notify)



if __name__ == u'__main__':
	def factory(dev):
		d = AMDevice(dev)
		d.connect()
		return d
	
	handle_devices(factory)





