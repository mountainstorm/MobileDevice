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
	u'''Represents a Apple Mobile Device; providing a wrapping around the raw
	MobileDeviceAPI.
	'''

	# XXX add recovery mode features - move them into anoher file

	INTERFACE_WIFI = 0 # XXX check this
	INTERFACE_USB = 1

	BUDDY_SETID = 0x1
	BUDDY_WIFI = 0x2

	value_domains = [
		u'com.apple.mobile.battery',
		u'com.apple.mobile.iTunes',
		u'com.apple.mobile.data_sync',
		u'com.apple.mobile.sync_data_class',
		u'com.apple.mobile.wireless_lockdown',
		u'com.apple.mobile.internal',
		u'com.apple.mobile.chaperone'
	]

	
	def __init__(self, dev):
		u'''Initializes a AMDevice object

		Arguments:
		dev -- the device returned by MobileDeviceAPI
		'''
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
			if AMDevicePair(self.dev) != MDERR_OK:
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
		On success, a location value e.g. the USB location ID

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

		Domains:
		AMDevice.value_domains
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
		u'''Puts the device into recovery mode

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

	def get_wireless_buddyflags(self):
		u'''Retrieve the wireless buddy flags; Probably used to do wifi sync

		Error:
		Raises a RuntimeError on error
		'''
		retval = None
		obj = c_long()
		if AMDeviceGetWirelessBuddyFlags(self.dev, byref(obj)) != MDERR_OK:
			raise RuntimeError(u'Unable to get wireless buddy flags')

		if obj is not None:
			retval = obj.value
		return retval

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

	def set_wireless_buddyflags(self, enable_wifi=True, setid=True):
		u'''Sets the wireless buddy flags, and optionally enables wifi

		Arguments:
		enable_wifi -- turns on/off wifi  (default True)
		setid -- if true, sets buddy id (default True)

		Error:
		Raises RuntimeError on error
		'''
		flags = 0
		if enable_wifi:
			flags |= AMDevice.BUDDY_WIFI
		if setid:
			flags |= AMDevice.BUDDY_SETID
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
	u'''Waits indefinatly handling devices arrival/removal events.
	
	Upon arrival the factory function will be called; providing the device as 
	a param.  This method should return an object on success, None on error.
	When the device is removed your object will have 'disconnect' called upon it

	Typical Example:
	def factory(dev):
		d = AMDevice(dev)
		d.connect()
		pprint.pprint(d.get_value())
		return d

	Arguments:
	factory - the callback function, called on device arrival

	Error:
	Raises a RuntimeError on error
	'''
	# XXX: what do I need to release
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

	# loop so we can exit easily
	while CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.1, False) == kCFRunLoopRunTimedOut:
		pass

	AMDeviceNotificationUnsubscribe(notify)


def list_devices(waittime=0.1):
	u'''Returns a dictionary of AMDevice objects, indexed by device id, 
	currently connected; waiting at least waittime for them to be discovered.

	Arguments:
	waittime - time to wait for devices to be discovered (default 0.1 seconds)
	'''
	# XXX: what do I need to release
	devices = {}

	def cbFunc(info, cookie):
		info = info.contents
		if info.message == ADNCI_MSG_CONNECTED:
			devices[info.device] = AMDevice(info.device)

	notify = AMDeviceNotificationRef()
	notifyFunc = AMDeviceNotificationCallback(cbFunc)
	err = AMDeviceNotificationSubscribe(notifyFunc, 0, 0, 0, byref(notify))
	if err != MDERR_OK:
		raise RuntimeError(u'Unable to subscribe for notifications')

	CFRunLoopRunInMode(kCFRunLoopDefaultMode, waittime, False)
	AMDeviceNotificationUnsubscribe(notify)
	return devices


def register_argparse_dev(cmdargs):
	import argparse
	import pprint

	# standard dev commands
	devparser = cmdargs.add_parser(
		u'dev', 
		help=u'commands related to the device'
	)

	def get_number_in_units(size,precision=2):
		suffixes = [u'b', u'kb', u'mb', u'gb']
		suffixIndex = 0
		while size > 1024:
			suffixIndex += 1 #increment the index of the suffix
			size = size / 1024.0 #apply the division
		return u'%.*f%s' % (precision,size,suffixes[suffixIndex])

	def cmd_info(args, dev):
		iface_types = {
			AMDevice.INTERFACE_USB: u'USB',
			AMDevice.INTERFACE_WIFI: u'WIFI'
		}
		print(u'  identifier: %s' % dev.get_deviceid())
		print(u'  interface type: %s' % iface_types[dev.get_interface_type()])
		print(u'  interface speed: %sps' % 
			get_number_in_units(int(dev.get_interface_speed()))
		)
		print(u'  location: 0x%x' % dev.get_location())
		print(u'  usb device id: 0x%x' % dev.get_usb_deviceid())
		print(u'  usb product id: 0x%x' % dev.get_usb_productid())
		
	def cmd_get(args, dev):
		if args.domain is not None or args.key is not None:
			key = None
			if args.key is not None:
				key = args.key.decode(u'utf-8')

			domain = None
			if args.domain is not None:
				domain = args.domain[0].decode(u'utf-8')
			pprint.pprint(dev.get_value(domain, key))
		else:
			# enumerate all the value_domains
			output = {}
			output[None] = dev.get_value()
			for domain in AMDevice.value_domains:
				output[domain] = dev.get_value(domain)
			pprint.pprint(output)

	def cmd_unpair(args, dev):
		dev.unpair()

	def cmd_buddy(args, dev):
		if args.wifi is not None or args.setid is not None:
			dev.set_wireless_buddyflags(args.wifi, args.setid)
		else:
			flags = dev.get_wireless_buddyflags()
			s = u''
			if flags & AMDevice.BUDDY_WIFI:
				s += u'BUDDY_WIFI'
			if flags & AMDevice.BUDDY_SETID:
				if len(s) != 0:
					s += u' | '
				s += u'BUDDY_SETID'
			s += u' (0x%x)' % flags
			print(u'  wireless buddy flags: %s' % s)

	# device info
	devcmds = devparser.add_subparsers()
	infocmd = devcmds.add_parser(
		u'info', 
		help=u'display basic info about the device'
	)
	infocmd.set_defaults(func=cmd_info)

	# get value
	getcmd = devcmds.add_parser(
		u'get', 
		help=u'display key/value info about the device'
	)
	getcmd.add_argument(
		u'key', 
		nargs=u'?',
		help=u'the key of the value to get'
	)
	getcmd.add_argument(
		u'-d', 
		metavar=u'domain', 
		dest=u'domain', 
		action=u'append',
		help=u'the domain of the keys to get'
	)
	getcmd.set_defaults(func=cmd_get)

	# unpair
	unpaircmd = devcmds.add_parser(
		u'unpair',
		help=u'unpair the device from this host'
	)
	unpaircmd.set_defaults(func=cmd_unpair)

	# set buddy id
	buddycmd = devcmds.add_parser(
		u'buddy',
		help=u'get/set wireless buddy parameters'
	)
	buddycmd.add_argument(
		u'-w', 
		help=u'enable wifi (0 or 1)', 
		dest=u'wifi', 
		type=int,
		choices=(0, 1)
	)
	buddycmd.add_argument(
		u'-s', 
		help=u'sets buddy id (0 or 1)', 
		dest=u'setid',
		type=int,		
		choices=(0, 1)
	)
	buddycmd.set_defaults(func=cmd_buddy)

	# XXX set/remove value
	# XXX activate, deactivate - do we really want to be able to do these?

