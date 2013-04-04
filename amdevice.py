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
import socket


class AMDevice(object):
	LOCATION_USB = 1

	INTERFACE_WIFI = 0 # TODO: check this
	INTERFACE_USB = 1
	
	def __init__(self, dev):
		self.dev = dev

	def activate(self, activation_record):
		u'''Sends the activation record to the device - activating it for use

		Arguments:
		activation_record -- the activation record, this will be converted to 
							 a CFType

		Error:
		Raises RuntimeError on error
		'''
		record = CFTypeFrom(activation_record)
		retval = AMDeviceActivate(self.dev, record)
		CFRelease(record)
		if retval != MDERR_OK:
			raise RuntimeError(u'Unable to activate the device')

	def connect(self):
		u'''Connects to the device, creates pairing record and starts a session

		Error:
		Raises RuntimeError describing the error condition
		'''
		if AMDeviceConnect(self.dev) != MDERR_OK: 
			raise RuntimeError(u'Unable to connect to device')

		if AMDeviceIsPaired(self.dev) != 1:
			raise RuntimeError(u'If your phone is locked with a passcode, unlock then reconnect it')

		if AMDeviceValidatePairing(self.dev) != MDERR_OK: 
			raise RuntimeError(u'Unable to validate pairing')

		if AMDeviceStartSession(self.dev) != MDERR_OK: 
			raise RuntimeError(u'Unable to start session')

	def get_deviceid(self):
		u'''Retrieves the device identifier; labeled "Identifier" in the XCode
		organiser; a 10 byte value as a string in hex

		Return:
		On success, the name as a string

		Error:
		Raises RuntimeError on error
		'''
		# AMDeviceGetName and AMDeviceCopyDeviceIdentifier return the same value
		# AMDeviceRef + 20
		cf = AMDeviceGetName(self.dev)
		if cf is None:
			raise RuntimeError(u'Unable to get device id')
		return CFTypeTo(cf)

	def get_location(self):
		u'''Retrieves the location of the device; the address on the interface
		(see get_interface_type)

		Return:
		On success, a AMDevice.LOCATION_* value on success

		Error:
		Raises RuntimeError on error		
		'''
		# AMDeviceCopyDeviceLocation and AMDeviceUSBLocationID both return 
		# same value
		# AMDeviceRef + 12
		retval = AMDeviceCopyDeviceLocation(self.dev)
		if retval is None:
			raise RuntimeError(u'Unable to get device location')
		return retval

	def get_value(self, domain=None, name=None):
		u'''Retrieves a value from the device

		Arguments:
		domain -- the domain to retrieve, or None to retrieve default domain
		          (default None)
		name -- the name of the value to retrieve, or None to retrieve all 
		        (default None)

		Return:
		On success the requested value
		
		Error:
		Raises RuntimeError on error

		TODO:
		Figure out valid domains
		'''
		retval = None
		cfdomain = None
		cfname = None
		if domain is not None:
			cfdomain = CFTypeFrom(domain)
		if name is not None:
			cfname = CFTypeFrom(name)
		value = AMDeviceCopyValue(self.dev, cfdomain, cfname)
		if cfdomain is not None: 
			CFRelease(cfdomain)
		if cfname is not None:
			CFRelease(cfname)
		if value is None:
			raise RuntimeError(u'Unable to retrieve value', domain, name)
		retval = CFTypeTo(value)
		CFRelease(value)
		return retval

	def deactivate(self):
		u'''Deactivates the device - removing it from the network.  WARNING: 
		you probably don't want to do this.

		Error:
		Raises RuntimeError on error
		'''
		if AMDeviceDeactivate != MDERR_OK:
			raise RuntimeError(u'Unable to deactivate the device')

	def disconnect(self):
		u'''Disconnects from the device, ending the session'''
		if self.dev is not None:
			AMDeviceStopSession(self.dev)
			AMDeviceDisconnect(self.dev)
			AMDeviceRelease(self.dev)
			self.dev = None

	def enter_recovery_mode(self):
		u'''Puts the device inot recovery mode

		Error:
		Raises RuntimeError on error'''
		if AMDeviceEnterRecovery(self.dev) != MDERR_OK:
			raise RuntimeError(u'Unable to put device in recovery mode')

	def get_interface_speed(self):
		u'''Retrieves the interface speed'''
		return AMDeviceGetInterfaceSpeed(self.dev)

	def get_interface_type(self):
		u'''Retrieves the interface type

		Return:
		None or error, else a AMDevice.INTERFACE_* value on success
		'''
		# AMDeviceRef + 24
		retval = AMDeviceGetInterfaceType(self.dev)
		if retval == -1:
			retval = None
		return retval

	def get_wireless_buddyid(self):
		u'''Retrieve the wireless buddy id; Probably used to do wifi sync

		Error:
		Raises a RuntimeError on error
		'''
		retval = None
		obj = CFTypeRef()
		if AMDeviceGetWirelessBuddyFlags(self.dev, byref(obj)) != MDERR_OK:
			raise RuntimeError(u'Unable to get wireless buddy id')
		return CFTypeTo(obj)

	def remove_value(self, domain, name):
		u'''Removes a value from the device

		Arguments:
		domain -- the domain to retrieve, or None to retrieve default domain
		          (default None)
		name -- the name of the value to retrieve, or None to retrieve all 
		        (default None)

		Error:
		Raises RuntimeError on error
		'''
		cfdomain = None
		cfname = None
		if domain is not None:
			cfdomain = CFTypeFrom(domain)
		if name is not None:
			cfname = CFTypeFrom(name)
		retval = AMDeviceRemoveValue(self.dev, cfdomain, cfname)
		if cfdomain is not None: 
			CFRelease(cfdomain)
		if cfname is not None:
			CFRelease(cfname)
		if value is not None:
			retval = CFTypeTo(value)
			CFRelease(value)
		if retval != MDERR_OK:
			raise RuntimeError(u'Unable to remove value %s/%s' % (domain, name))

	def set_value(self, domain, name, value):
		u'''Sets a value on the device

		Arguments:
		domain -- the domain to retrieve, or None to retrieve default domain
		          (default None)
		name -- the name of the value to retrieve, or None to retrieve all 
		        (default None)

		Error:
		Raises RuntimeError on error
		'''
		cfdomain = None
		cfname = None
		if domain is not None:
			cfdomain = CFTypeFrom(domain)
		if name is not None:
			cfname = CFTypeFrom(name)
		if value is not None:
			cfvalue = CFTypeFrom(value)
		retval = AMDeviceRemoveValue(self.dev, cfdomain, cfname, cfvalue)
		if cfdomain is not None: 
			CFRelease(cfdomain)
		if cfname is not None:
			CFRelease(cfname)
		if cfvalue is not None:
			CFRelease(cfvalue)
		if retval != MDERR_OK:
			raise RuntimeError(u'Unable to set value %s/%s' % (domain, name, value))

	def set_wireless_buddyid(self, enable_wifi=True, setid=True):
		u'''Sets the wireless buddyid from iTunes, and optionally enables wifi

		Arguments:
		enable_wifi -- turns on/off wifi if there a buddy id (default True)
		setid -- if true, sets buddy id (default True)

		Error:
		Raises RuntimeError on error
		'''
		flags = 0
		if enable_wifi:
			flags |= 0x2
		if setid:
			flags |= 0x1
		if AMDeviceSetWirelessBuddyFlags(self.dev, flags) != MDERR_OK:
			raise RuntimeError(u'Unable to set buddy id flags', enable_wifi, setid)

	def start_service(self, service_name, options=None):
		u'''Starts the service and returns the socket

		Argument:
		service_name -- the reverse domain name for the service
		options -- a dict of options, or None (default None)

		Return:
		The OS socket associated with the connection to the service

		Error:
		Raises RuntimeError on error
		''' 
		sock = c_int32()
		if AMDeviceStartServiceWithOptions(
				self.dev, 
				service_name, 
				options,
				byref(sock)
			) != MDERR_OK:
			raise RuntimeError(u'Unable to start service %s' % service_name)
		return sock.value

	def get_usb_deviceid(self):
		u'''Retrieves the USB device id

		Return:
		The usb device id

		Error:
		Raises RuntimeError if theres no usb device id
		'''
		# AMDeviceRef + 8
		retval = AMDeviceUSBDeviceID(self.dev)
		if retval == 0:
			raise RuntimeError(u'No usb device id')
		return retval

	def get_usb_productid(self):
		u'''Retrieves the USB product id

		Return:
		The usb product id

		Error:
		Raises RuntimeError if theres no usb product id
		'''
		# AMDeviceRef + 16
		retval = AMDeviceUSBProductID(self.dev)
		if retval == 0:
			raise RuntimeError(u'No usb device id')
		return retval

	def unpair(self):
		u'''Unpairs device from host WARNING: you probably dont want to call 
		this

		Error:
		Raises RuntimeError on error
		'''
		if AMDeviceUnpair(self.dev) != MDERR_OK:
			raise RuntimeError(u'Unable to unpair device')

	def connect_to_port(self, port):
		u'''Connects to a listening TCP port on the device.

		Error:
		Raises RuntimeError on error
		'''
		sock = c_int32()
		# logic taken from _connect_to_port
		if self.get_interface_type() == AMDevice.INTERFACE_USB:
			if USBMuxConnectByPort(
					self.get_usb_deviceid(),
					socket.htons(port), 
					byref(sock)
				) != MDERR_OK:
				raise RuntimeError(u'Unable to connect to socket via usb')
		else:
			# TODO: test!
			if AMDeviceConnectByAddressAndPort(
					self.dev, 
					port, 
					byref(sock)
				) != MDERR_OK:
				raise RuntimeError(u'Unable to connect to socket')
		return sock.value



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
	import pprint
	import os

	def factory(dev):
		d = AMDevice(dev)
		d.connect()
		pprint.pprint(d.get_value())
		print d.get_usb_deviceid()
		print d.get_usb_productid()
		print d.get_interface_type()
		print d.get_interface_speed()
		print d.get_deviceid()
		print u'%x' % d.get_location()
		print
		pprint.pprint(d.get_value(u'com.apple.'))

		s = d.connect_to_port(62078)
		print u'open socket to lockdownd: %d' % s
		os.close(s)

		return d
	
	handle_devices(factory)





