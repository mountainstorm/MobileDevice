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
import time


class CrashMover(object):
	u'''Moves crash logs from their various scattered locations into the afc 
	crash log directory'''

	def __init__(self, amdevice):
		self.s = amdevice.start_service(u'com.apple.crashreportmover')
		if self.s is None:
			raise RuntimeError(u'Unable to launch: com.apple.crashreportmover')

	def disconnect(self):
		os.close(self.s)

	def move_crashlogs(self, extensions=None):
		u'''Moves all crash logs into the afc crash log directory

		Arguments:
		extensions -- if present a list of crash file extensions to move 
					  XXX not currently working
		'''
		# XXX should we wait just in case?
		time.sleep(2)
		buf = os.read(self.s, 1)
		while True:
			buf += os.read(self.s, 1)
			if buf == 'ping':
				break # done!


def register_argparse_crashmover(cmdargs):
	import argparse
	import sys

	def cmd_crashmove(args, dev):
		cm = CrashMover(dev)
		cm.move_crashlogs()
		cm.disconnect()
		dev.disconnect()

	# cmd_crashmove command
	crashmovecmd = cmdargs.add_parser(
		u'crashmove', 
		help=u'moves crash logs into the afc directory'
	)
	crashmovecmd.set_defaults(func=cmd_crashmove)
