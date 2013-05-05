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


from amdevice import *
from afc import *


class AFCMediaDirectory(AFC):
	def __init__(self, amdevice):
		s = amdevice.start_service(AMSVC_AFC)
		if s is None:
			raise RuntimeError(u'Unable to launch:', AMSVC_AFC)
		AFC.__init__(self, s)

	def transfer_application(self, path, progress=None):
		u'''Transfers an application bundle to the device; into the 
		/PublicStaging directory

		Arguments:
		path -- the local path to the file to transfer
		progress -- the callback to get notified of the transfer process
		            (defaults to none)

		Error:
		Raises RuntimeError on error
		'''
		# Technically you could use this on any AFC connection but it only makes
		# sense to use it on the MediaDirectory - as it hard coded moves stuff 
		# to /PublicStaging
		def callback(cfdict, arg):
			pass

		cfpath = CFTypeFrom(path)
		cb = AFCProgressCallback(callback)
		if progress is not None:
			cb = AFCProgressCallback(progress)
		err = AMDeviceTransferApplication(self.s, cfpath, None, cb, None)
		CFRelease(cfpath)
		if err != MDERR_OK:
			raise RuntimeError(u'Unable to transfer application')


def register_argparse_afc(cmdargs):
	import argparse
	import sys
	import afcapplicationdirectory
	import afccrashlogdirectory
	import afcmediadirectory
	import afcroot
	import time

	def printdir(afc, path, recurse):
		dirlist = []
		for name in afc.listdir(path):
			isdir = u''
			info = afc.lstat(path + name)
			if info.st_ifmt == stat.S_IFDIR:
				isdir = u'/'
				dirlist.append(path + name + isdir)

			types = {
				stat.S_IFSOCK: u's',
				stat.S_IFLNK: u'l',
				stat.S_IFREG: u'-',
				stat.S_IFBLK: u'b',
				stat.S_IFDIR: u'd',
				stat.S_IFCHR: u'c',
				stat.S_IFIFO: u'p'
			}
			t = time.asctime(time.gmtime(float(info.st_mtime)))
			print(types[info.st_ifmt] + u' ' + t + u' ' + info.st_size + u' ' + name + isdir)
		if recurse:
			for name in dirlist:
				print(u'\n' + name)
				printdir(afc, name, recurse)

	def get_afc(args, dev):
		retval = None
		if args.m:
			retval = afcmediadirectory.AFCMediaDirectory(dev)
		elif args.c:
			retval = afccrashlogdirectory.AFCCrashLogDirectory(dev)
		elif args.app is not None:
			retval = afcapplicationdirectory.AFCApplicationDirectory(
				dev, 
				args.app.decode(u'utf-8')
			)
		else:
			retval = afcroot.AFCRoot(dev)
		return retval

	def cmd_ls(args, dev):
		afc = get_afc(args, dev)
		printdir(afc, args.path.decode(u'utf-8'), args.r)
		afc.disconnect()

	# afc command
	afcparser = cmdargs.add_parser(
		u'afc', 
		help=u'commands to manipulate files via afc'
	)
	afcgroup = afcparser.add_mutually_exclusive_group()
	afcgroup.add_argument(
		u'-a',
		metavar=u'app',
		dest=u'app',
		help=u'reverse domain name of application; device paths become relative to app container'
	)
	afcgroup.add_argument(
		u'-c',
		action=u'store_true',
		help=u'crashlogs; device paths become relative to crash log container'
	)
	afcgroup.add_argument(
		u'-m',
		action=u'store_true',
		help=u'device paths become relative to /var/mobile/media (saves typing)'
	)
	afccmd = afcparser.add_subparsers()

	# ls command
	lscmd = afccmd.add_parser(
		u'ls',
		help=u'lists the contents of the directory'
	)
	lscmd.add_argument(
		u'-r',
		action=u'store_true',
		help=u'if specified listing is recursive'
	)
	lscmd.add_argument(
		u'path',
		help=u'path on the device to list'
	)
	lscmd.set_defaults(func=cmd_ls)


#if __name__ == u'__main__':
#	import sys
#
#	
#	def factory(dev):
#		d = AMDevice(dev)
#		d.connect()
#		afc = AFCMediaDirectory(d)
#		printdir(afc, u'/') # recursive print of all files visible
#
#		AMDSetLogLevel(0xff)
#		afc.transfer_application(u'/Users/cooper/Documents/Dev/iOS/DeveloperDiskImg/Applications/MobileReplayer.app')
#		AMDSetLogLevel(0x0)
#
#		printdir(afc, u'/') # recursive print of all files visible
#
#		afc.disconnect()
#		return d
#	
#	handle_devices(factory)

