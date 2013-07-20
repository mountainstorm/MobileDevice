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
	import afccrashlogdirectory
	import posixpath
	import stat

	def cmd_crashmove(args, dev):
		cm = CrashMover(dev)
		cm.move_crashlogs()
		cm.disconnect()

	def get_logs(afc, path, dest):
		dirlist = []
		for name in afc.listdir(path):
			info = afc.lstat(posixpath.join(path, name))
			if info.st_ifmt == stat.S_IFDIR:
				dirlist.append((
					posixpath.join(path, name),
					os.path.join(dest, name)
				))
				try:
					os.mkdir(os.path.join(dest, name))
				except OSError:
					pass # it already exists
			elif info.st_ifmt == stat.S_IFLNK:
				pass # XXX handle symlinks e.g. LatestCrash*
			else:
				s = afc.open(posixpath.join(path, name), u'r')
				d = open(os.path.join(dest, name), u'w+')
				d.write(s.readall())
				d.close()
				s.close()
		for names in dirlist:
			get_logs(afc, names[0], names[1])

	def del_logs(afc, path):
		dirlist = []
		for name in afc.listdir(path):
			info = afc.lstat(posixpath.join(path, name))
			if info.st_ifmt == stat.S_IFDIR:
				dirlist.append(posixpath.join(path, name))
			else:
				afc.remove(posixpath.join(path, name))

		for name in dirlist:
			del_logs(afc, name)
			afc.remove(name)

	def cmd_crashget(args, dev):
		# move the crashes
		cm = CrashMover(dev)
		cm.move_crashlogs()
		cm.disconnect()

		# retrieve the crashes
		afc = afccrashlogdirectory.AFCCrashLogDirectory(dev)
		get_logs(afc, u'/', args.dest.decode(u'utf-8'))

		# optionally, delete the crashes
		if args.delete_logs:
			del_logs(afc, u'/')
		afc.disconnect()

	# cmd_crashmove command
	crashparser = cmdargs.add_parser(
		u'crash', 
		help=u'manipulates crash logs'
	)

	crashcmd = crashparser.add_subparsers()

	crashmovecmd = crashcmd.add_parser(
		u'move', 
		help=u'moves crash logs into the afc directory'
	)
	crashmovecmd.set_defaults(func=cmd_crashmove)

	# get the crash logs
	crashgetcmd = crashcmd.add_parser(
		u'get', 
		help=u'retrieves crash logs from the device'
	)
	crashgetcmd.add_argument(
		u'-d',
		dest=u'delete_logs',
		action=u'store_true',
		help=u'if specified, delete the crash logs after retrieval'
	)
	crashgetcmd.add_argument(
		u'dest',
		help=u'destination directory; files are appended into it'
	)	
	crashgetcmd.set_defaults(func=cmd_crashget)
