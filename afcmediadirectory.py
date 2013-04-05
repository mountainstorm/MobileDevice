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


if __name__ == u'__main__':
	import sys

	def printdir(afc, path):
		for name in afc.listdir(path):
			isdir = u''
			if afc.lstat(path + name).st_ifmt == stat.S_IFDIR:
				isdir = u'/'
			print path + name + isdir
			if afc.lstat(path + name).st_ifmt == stat.S_IFDIR:
				printdir(afc, path + name + isdir)
	
	def factory(dev):
		d = AMDevice(dev)
		d.connect()
		afc = AFCMediaDirectory(d)
		printdir(afc, u'/') # recursive print of all files visible

		AMDSetLogLevel(0xff)
		afc.transfer_application(u'/Users/cooper/Documents/Dev/iOS/DeveloperDiskImg/Applications/MobileReplayer.app')
		AMDSetLogLevel(0x0)

		printdir(afc, u'/') # recursive print of all files visible

		afc.disconnect()
		return d
	
	handle_devices(factory)

