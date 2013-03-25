MobileDevice.py
---------------

A python package which wraps Apple's MobileDevice API.  

The basic structure of the package is as follows:

MobileDevice.py: this is a bare bones ctypes wrapper over the native C library; 
see here for documentation of the basic API
http://theiphonewiki.com/wiki/MobileDevice_Library#MobileDevice_Header_.28MobileDevice.h.29

CoreFoundation.py: this is a simple ctypes wrapper around CoreFoundation and a
few helper methods to convert between CFTypes and python types


All other classes:
afc.py, syslog.py, filerelay.py, amdevice.py etc are more pythonic wrappers
around the base C library.

The idea being that we give a python abstraction of all the services e.g.


To list all files on the file system:
-------------------------------------
from MobileDevice import *

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
	afc = AFC(d)

	printdir(afc, u'/') # recursive print of all files visible

	afc.disconnect()
	return d

handle_devices(factory)


To retrieve a .cpio.gz file of all the readonly special data (crashlogs etc)
----------------------------------------------------------------------------
from MobileDevice import *

def factory(dev):
	d = AMDevice(dev)
	d.connect()
	fr = FileRelay(d)

	f = open(u'dump.cpio.gz', 'wb')
	f.write(fr.retrieve([
		u'AppleSupport',
		u'Network',
		u'VPN',
		u'WiFi',
		u'UserDatabases',
		u'CrashReporter',
		u'tmp',
		u'SystemConfiguration'
	]))
	f.close()

	fr.disconnect()
	return d

handle_devices(factory)


To read and print all syslog messages
-------------------------------------
from MobileDevice import *
import sys

def factory(dev):
	d = AMDevice(dev)
	d.connect()
	sl = Syslog(d)

	while True:
		msg = sl.read()
		if msg is None:
			break
		sys.stdout.write(msg)

	sl.disconnect()
	return d

handle_devices(factory)


Copyright
---------

Copyright (c) 2013 Mountainstorm

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
