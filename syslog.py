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


class Syslog(object):
	u'''Syslog relay class; starts the syslog service and reads all entries'''

	def __init__(self, amdevice):
		self.s = amdevice.start_service(AMSVC_SYSLOG_RELAY)
		if self.s is None:
			raise RuntimeError(u'Unable to launch:', AMSVC_SYSLOG_RELAY)

	def disconnect(self):
		os.close(self.s)

	def read(self, length=1024):
		u'''reads at most length bytes from the syslog; blocking if no more data
		is avaliable

		Arguments:
		length -- the max bytes to read (default 1024)
		'''
		return os.read(self.s, length)


def register_argparse_syslog(cmdargs):
	import argparse
	import sys

	def cmd_syslog(args, dev):
		sl = Syslog(dev)
		while True:
			msg = sl.read()
			if msg is None:
				break
			sys.stdout.write(msg)
		sl.disconnect()

	# syslog command
	syslogcmd = cmdargs.add_parser(
		u'syslog', 
		help=u'displays syslog info from the device'
	)
	syslogcmd.set_defaults(func=cmd_syslog)
