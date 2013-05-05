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


u'''command line tool interface'''


if __name__ == u'__main__':
	import os
	import sys
	import argparse
	from __init__ import *

	#	s = d.connect_to_port(62078)
	#	print u'open socket to lockdownd: %d' % s
	#	os.close(s)

	class CmdArguments(object):
		def __init__(self):
			self._devs = list_devices()
			for v in self._devs.values():
				v.connect()

			self._parser = argparse.ArgumentParser()

			self._parser.add_argument(
				u'-d', 
				metavar=u'DEVID',
				dest=u'device_idx',
				choices=range(len(self._devs.keys())),
				type=int,
				action=u'append',
				help=u'only operate on the specified device'
			)
			
			# add subparsers for commands
			self._subparsers = self._parser.add_subparsers(
				help=u'sub-command help; use <cmd> -h for help on sub commands'
			)
			
			# add listing command
			listparser = self._subparsers.add_parser(
				u'list', 
				help=u'list all attached devices'
			)
			listparser.set_defaults(listing=True)


		def __del__(self):
			for v in self._devs.values():
				v.disconnect()

		def add_parser(self, *args, **kwargs):
			return self._subparsers.add_parser(*args, **kwargs)

		def parse_args(self):
			args = self._parser.parse_args(namespace=self)
			i = 0
			if u'listing' in dir(self):
				sys.stdout.write(self._print_devices())

			else:
				if len(self._devs) > 0:
					if self.device_idx is None:
						self.device_idx = 0 # default to first device
					k = sorted(self._devs.keys())[self.device_idx]
					v = self._devs[k]
					name = u''
					try:
						name = v.get_value(name=u'DeviceName')
					except:
						pass
					print(u'%u: %s - "%s"' % (
						self.device_idx, 
						v.get_deviceid(), 
						name.decode(u'utf-8')
					))
					args.func(args, v)

		def _print_devices(self):
			retval = u'device list:\n'
			i = 0
			for k in sorted(self._devs.keys()):
				v = self._devs[k]
				try:
					name = v.get_value(name=u'DeviceName')
					retval += u'  %u: %s - "%s"\n' % (
						i, 
						v.get_deviceid(), 
						name.decode(u'utf-8')
					)
				except:
					retval += u'  %u: %s\n' % (i, k)
				i = i + 1
			return retval			


	cmdargs = CmdArguments()

	# register any command line arguments from the modules
	for member in dir():
		if member.startswith(u'register_argparse_'):
			globals()[member](cmdargs)

	cmdargs.parse_args()
