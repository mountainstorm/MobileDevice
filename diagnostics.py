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
	u'''Communicates with the diagnostic service and allows retrival of 
	diagnostic information
	'''

	TYPE_ALL = u'All'
	TYPE_WIFI = u'WiFi'
	TYPE_GASGAUGE = u'GasGauge'
	TYPE_NAND = u'NAND'

	ACTION_WAIT_FOR_DISCONNECT = u'WaitForDisconnect'
	ACTION_DISPLAY_PASS = u'DisplayPass'
	ACTION_DISPLAY_FAIL = u'DisplayFail'

	gestalt_names = [
	]

	def __init__(self, amdevice):
		PlistService.__init__(
			self,
			amdevice, 
			[AMSVC_MOBILE_DIAGNOSTICS_RELAY, AMSVC_IOSDIAGNOSTICS_RELAY],
			kCFPropertyListXMLFormat_v1_0
		)

	def disconnect(self):
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
		if u'Status' in result and result[u'Status'] == u'Success':
			retval = True
		return retval

	def sleep(self):
		u'''Sends the device to sleep; disconnecting it from the host'''
		self._sendmsg({u'Request': u'Sleep'})
		return self._chkresult(self._recvmsg())

	def restart(self, actions=[]):
		u'''Restarts the device'''
		return self._action(u'Restart', actions)

	def shutdown(self, actions=[]):
		u'''Shutsdownt the host'''
		return self._action(u'Shutdown', actions)

	def diagnostics(self, typ):
		u'''Retrieves diagnostic information from the device; i.e. gasguage,
		wifi, nand.

		Arguments:
		typ -- one of the ACTION_* defines
		'''
		retval = None
		self._sendmsg({u'Request': typ})
		msg = self._recvmsg()
		if self._chkresult(msg):
			retval = msg[u'Diagnostics']
		return retval

	# look in com.apple.mobilegestalt.plist for values
	def mobilegestalt(self, keys):
		u'''Retrieves mobile gestalt values

		Arguments:
		keys -- an array of keys to retrieve
		'''
		self._sendmsg({
			u'Request': u'MobileGestalt',
			u'MobileGestaltKeys': keys
		})
		msg = self._recvmsg()
		if self._chkresult(msg):
			retval = msg[u'Diagnostics'][u'MobileGestalt']
		return retval

	# IODeviceTree, IOPower, IOService
	def ioregistry(self, plane=u'IOService', name=None, cls=None):
		u'''Retrieves IORegistry keys and values

		Arguments:
		plane -- a IOReg plane name; IODeviceTree, IOPower, IOService
		name -- the name of the key to retrieve
		cls -- the class of the key to retrieve
		'''
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


def register_argparse_diag(cmdargs):
	import argparse
	import pprint
	import sys

	def ioreg_dmp(d, pad=u'  '):
		# XXX should really adjust to get rid of all the -2's
		if isinstance(d, list):
			sys.stdout.write(u'[\n')
			for i in range(len(d)):
				sys.stdout.write(pad)
				ioreg_dmp(d[i], pad + u'  ')
			sys.stdout.write(pad[:-2] + u']\n')
		elif isinstance(d, dict):
			i = 0
			if u'regEntry' in d:
				# its a reg entry
				inheritance = d[u'inheritance'].replace(u' : ', u':')
				sys.stdout.write(
					u'+-o ' + d[u'name'] + u'  <class ' + inheritance + u', ' + d[u'state'] + u'>\n'
				)
				op = pad
				if len(d[u'children']) > 0:
					pad += u'| '
				else:
					pad += u'  '
				sys.stdout.write(pad)
				ioreg_dmp(d[u'properties'], pad + u'  ')
				sys.stdout.write(pad + u'\n')
				i = 0
				for c in d[u'children']:
					if i == len(d[u'children'])-1:
						pad = pad[:-2] + u'  '
					sys.stdout.write(pad[:-2])
					ioreg_dmp(c, pad)
					i += 1
			else:
				# something else?
				sys.stdout.write(u'{\n')
				for k, v in d.iteritems():
					sys.stdout.write(pad + u'"' + k + u'" = ')
					ioreg_dmp(v, pad + u'  ')
				sys.stdout.write(pad[:-2] + u'}\n')
		elif isinstance(d, unicode):
			sys.stdout.write(u'"' + d + u'"\n')
		elif isinstance(d, str):
			# dont know why but some strings name/inheritence etc come back as 
			# CFData rather then CFString's - so we'll try to convert; if it 
			# doesn't look like a string
			isdata = False
			nullterm = False
			for c in d:
				if nullterm == True and ord(c) != 0:
					isdata = True
					break
				if ord(c) == 0:
					nullterm = True
				elif ord(c) < 32 or ord(c) > 127:
					isdata = True
					break
			if isdata:
				sys.stdout.write(d.encode(u'hex') + u'\n')
			else:
				sys.stdout.write(u'"' + d + u'"\n')				
		elif isinstance(d, (int, long, float, complex)):
			sys.stdout.write(d.__str__() + u'\n')
		else:
			print type(d)
			pprint.pprint(d)

	def cmd_gestalt(args, dev):
		diag = Diagnostics(dev)
		if args.name is not None:
			print(diag.mobilegestalt([args.name.decode(u'utf-8')]))
		else:
			print(diag.mobilegestalt(Diagnostics.gestalt_names))
		diag.disconnect()

	def cmd_all(args, dev):
		diag = Diagnostics(dev)
		pprint.pprint(diag.diagnostics(Diagnostics.TYPE_ALL))
		diag.disconnect()

	def cmd_ioreg(args, dev):
		diag = Diagnostics(dev)
		plane = u'IOService'
		name = None
		cls = None
		# XXX check the name/cls params actually work
		if args.plane is not None:
			plane = args.plane.decode(u'utf-8')
		if args.name is not None:
			name = args.name.decode(u'utf-8')
		if args.cls is not None:
			cls = args.cls.decode(u'utf-8')
		ioreg_dmp(diag.ioregistry(plane, name, cls)[u'IORegistry'])
		diag.disconnect()		

	def cmd_sleep(args, dev):
		diag = Diagnostics(dev)
		diag.sleep()
		diag.disconnect()

	def cmd_restart(args, dev):
		diag = Diagnostics(dev)
		if args.quick:
			diag.restart([Diagnostics.ACTION_DISPLAY_FAIL])
		else:
			diag.restart([Diagnostics.ACTION_DISPLAY_PASS])
		diag.disconnect()

	def cmd_shutdown(args, dev):
		diag = Diagnostics(dev)
		print args.quick
		if args.quick:
			diag.shutdown([Diagnostics.ACTION_DISPLAY_FAIL])
		else:
			diag.shutdown([Diagnostics.ACTION_DISPLAY_PASS])
		diag.disconnect()

	# diag command
	diagparser = cmdargs.add_parser(
		u'diag', 
		help=u'retrieves diagnostic info; includes state changes like reboot, sleep etc'
	)
	diagcmd = diagparser.add_subparsers()

	# mobile gestalt command
	gestaltcmd = diagcmd.add_parser(
		u'gestalt',
		help=u'retrieves mobile gestalt values'
	)
	gestaltcmd.add_argument(
		u'name',
		nargs=u'?',
		help=u'the name of the gestalt value to retrieve'
	)
	gestaltcmd.set_defaults(func=cmd_gestalt)

	# all command
	allcmd = diagcmd.add_parser(
		u'all',
		help=u'retrieves all diagnostic info; gasguage, wifi and nand'
	)
	allcmd.set_defaults(func=cmd_all)

	# ioreg command
	ioregcmd = diagcmd.add_parser(
		u'ioreg',
		help=u'retrieves ioregistry information from the device; defaults to the IOService plane'
	)
	ioregcmd.add_argument(
		u'-p',
		metavar=u'plane',
		dest=u'plane',
		help=u'the ioregistry plane to retrieve; IODeviceTree, IOPower, IOService etc'
	)
	ioregcmd.add_argument(
		u'-n',
		metavar=u'name',
		dest=u'name',
		help=u'ioregistry entry name to retrieve'
	)
	ioregcmd.add_argument(
		u'-c',
		metavar=u'class',
		dest=u'cls',
		help=u'ioregistry entry class to retrieve'
	)
	ioregcmd.set_defaults(func=cmd_ioreg)

	# sleep command
	sleepcmd = diagcmd.add_parser(
		u'sleep',
		help=u'put the device to sleep'
	)
	sleepcmd.set_defaults(func=cmd_sleep)

	# restart command
	restartcmd = diagcmd.add_parser(
		u'restart',
		help=u'restarts the device'
	)
	restartcmd.add_argument(
		u'-q',
		dest=u'quick',
		action=u'store_true',
		help=u'restarts quickly - without properly shutting down'
	)	
	restartcmd.set_defaults(func=cmd_restart)

	# shutdown command
	shutdowncmd = diagcmd.add_parser(
		u'shutdown',
		help=u'shutsdown the device'
	)
	shutdowncmd.add_argument(
		u'-q',
		dest=u'quick',
		action=u'store_true',
		help=u'shutsdown quickly'
	)	
	shutdowncmd.set_defaults(func=cmd_shutdown)

