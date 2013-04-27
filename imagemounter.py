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


class ImageMounter(object):
	def __init__(self, amdevice):
		self.dev = amdevice

	def disconnect(self):
		pass

	def find_debug_image(self):
		u'''Returns the best debug disk image for the device

		Returns:
		the path of the .dmg

		Error:
		Raises RuntimeError if a suitable disk image can't be found
		'''
		# TODO: Windows version
		version = self.dev.get_value(name=u'ProductVersion')
		build = self.dev.get_value(name=u'BuildVersion')
		home = os.environ[u'HOME']
		ds = os.path.join(
			home, 
			u'/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/DeviceSupport/'
		)
		print u'%s %s' % (version, build)
		path = ds + u'%s (%s)/DeveloperDiskImage.dmg' % (version, build)
		if not os.path.exists(path):
			# try it without the build no
			path = ds + u'%s/DeveloperDiskImage.dmg' % (version)
			if not os.path.exists(path):
				raise RuntimeError(u'Unable to find developer disk image')
		return path

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
			pass

		if image_path is None:
			image_path = self.find_debug_image()

		sigpath = image_path + u'.signature'
		f = open(sigpath, u'rb')
		sig = f.read()
		f.close()

		cfpath = CFTypeFrom(image_path)
		cfoptions = CFTypeFrom({
			u'ImageType': u'Developer',
			u'ImageSignature': sig
		})

		cb = AMDeviceProgressCallback(callback)
		if progress is not None:
			cb = AMDeviceProgressCallback(progress)
		err = AMDeviceMountImage(self.dev.dev, cfpath, cfoptions, cb, None)
		CFRelease(cfpath)
		CFRelease(cfoptions)
		CFRelease(cfsig)
		if err != MDERR_OK:
			raise RuntimeError(u'Unable to mount disk image', err)


if __name__ == u'__main__':
	import sys

	def factory(dev):
		d = AMDevice(dev)
		d.connect()
		im = ImageMounter(d)

		AMDSetLogLevel(0xff)
		im.mount(u'/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/DeviceSupport/6.0 (10A403)/DeveloperDiskImage.dmg')

		im.disconnect()
		return d
	
	handle_devices(factory)

