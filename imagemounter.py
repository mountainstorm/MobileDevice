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
import os.path
import os
from plistservice import *


class ImageMounter(object):
	def __init__(self, amdevice):
		self.dev = amdevice

	def disconnect(self):
		pass

	def mount(self, image_path=None, progress=None):
		u'''Mounts a disk image on the device.

		Arguments:
		image -- the path to the image to load; the .signature file must be 
		         beside the image (default None - we select the best debug
		         disk image)
		progress -- an optional callback (default None)

		Error:
		Raises RuntimeError on mounting error, or a file exception from reading
		the signature file
		'''
		def callback(cfdict, arg):
			pass #print CFTypeTo(cfdict)

		if image_path is None:
			image_path = self.dev.find_developer_disk_image_path()

		sigpath = image_path + u'.signature'
		f = open(sigpath, u'rb')
		sig = f.read()
		f.close()

		cfpath = CFTypeFrom(image_path)
		cfoptions = CFTypeFrom({
			u'ImageType': u'Developer', # XXX add support for other image types
			u'ImageSignature': sig
		})
		cb = AMDeviceProgressCallback(callback)
		if progress is not None:
			cb = AMDeviceProgressCallback(progress)
		# XXX so the code for mount image checks if its mounted and only bothers
		# to resend the image if it isn't; for some reason I dont understand its
		# not doing this on my version - its always sending it; then the mount 
		# fails (with lots of syslog output on the device)
		# -- this may be due to the image I'm loading not being a perfect match
		#AMDSetLogLevel(0xff)
		err = AMDeviceMountImage(self.dev.dev, cfpath, cfoptions, cb, None)
		#AMDSetLogLevel(0x00)
		CFRelease(cfpath)
		CFRelease(cfoptions)
		if err != MDERR_OK and (err & 0xFFFFFFFF) != 0xe8000076: # already mounted
			raise RuntimeError(u'Unable to mount disk image', err)


def register_argparse_mount(cmdargs):
	import argparse
	import pprint
	import sys

	def cmd_mountdev(args, dev):
		im = ImageMounter(dev)
		im.mount()
		im.disconnect()

	def cmd_mountcustom(args, dev):
		im = ImageMounter(dev)
		im.mount(args.path.decode(u'utf-8'))
		im.disconnect()		

	mountparser = cmdargs.add_parser(
		u'mount',
		help=u'mounts a disk image'
	)
	mountcmds = mountparser.add_subparsers()

	# mount developer disk image
	devcmd = mountcmds.add_parser(
		u'dev',
		help=u'mounts the best developer disk image avaliable for the device'
	)
	devcmd.set_defaults(func=cmd_mountdev)

	# mount custom disk image
	cuscmd = mountcmds.add_parser(
		u'custom',
		help=u'mounts the supplied disk image; .signature file must be alongside'
	)
	cuscmd.add_argument(
		u'path',
		help=u'the path to the .dmg; we expect a .signature alongside'
	)
	cuscmd.set_defaults(func=cmd_mountcustom)


#'/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/DeviceSupport/6.0 (10A403)/DeveloperDiskImage.dmg'

