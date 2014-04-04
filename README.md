MobileDevice.py
===============

A python package which aims to wrap Apple's MobileDevice API; to provide 
complete support for all iOS, device services.

The project aims to provide both a native Pythin API (using ctypes) and a fully
features command line interface.

You can run the project directory as a package e.g.

**python MobileDevice/ afc put myfile.txt /var/mobile/Media/**

or:

**python MobileDevice.zip afc put myfile.txt /var/mobile/Media/**

or, if you install the library using: sudo python setup.py install

**mdf afc put myfile.txt /var/mobile/Media/**

(will upload a file to the device)

at any point append *-h* to the command line to get more help

In general I recommend you install the package if you're ever going to write 
scripts using it, or just fancy typing less characters.


Project Structure
-----------------

The basic structure of the package is as follows:

MobileDevice.py: this is a bare bones ctypes wrapper over the native C library

CoreFoundation.py: this is a simple ctypes wrapper around CoreFoundation and a
few helper methods to convert between CFTypes and python types

All other classes:
afc.py, syslog.py, filerelay.py, amdevice.py etc are more pythonic wrappers
around the base C library.

The idea being that we give a python abstraction of all the services e.g.


To list all files on the file system:
-------------------------------------
from command line:

**mdf afc ls /var/mobile/Media**

or in code:

	from MobileDevice import *

	def printdir(afc, path):
		for name in afc.listdir(path):
			isdir = u''
			if afc.lstat(path + name).st_ifmt == stat.S_IFDIR:
				isdir = u'/'
			print path + name + isdir
			if afc.lstat(path + name).st_ifmt == stat.S_IFDIR:
				printdir(afc, path + name + isdir)
	
	dev = list_devices()[0]
	dev.connect()
	afc = AFC(dev)

	printdir(afc, u'/var/mobile/Media') # recursive print of all files visible

	afc.disconnect()


To retrieve a .cpio.gz file of all the readonly special data (crashlogs etc)
----------------------------------------------------------------------------
from command line:

**mdf filerelay dump.cpio.gz**

or in code:

	from MobileDevice import *

	dev = list_devices()[0]
	dev.connect()
	fr = FileRelay(dev)

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


To read and print all syslog messages
-------------------------------------
from command line:

**mdf syslog**

or in code:

	from MobileDevice import *
	import sys

	dev = list_devices()[0]
	dev.connect()
	sl = Syslog(dev)

	while True:
		msg = sl.read()
		if msg is None:
			break
		sys.stdout.write(msg)

	sl.disconnect()


Keywords
--------
iOS, iPad, iPhone, Apple, MobileDevice, python, command line, lockdownd, 
usbmuxd
