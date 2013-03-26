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
from plistservice import *


class Springboard(PlistService):
	PORTRAIT = 1
	PORTRAIT_UPSIDE_DOWN = 2 
	LANDSCAPE = 3 # home button to right
	LANDSCAPE_HOME_TO_LEFT = 4

	def __init__(self, amdevice):
		PlistService.__init__(
			self, 
			amdevice, 
			[AMSVC_SPRINGBOARD_SERVICES]
		)

	def get_iconstate(self):
		self._sendmsg({u'command': u'getIconState'})
		return self._recvmsg()

	def set_iconstate(self, state):
		self._sendmsg({
			u'command': u'setIconState',
			u'iconState': state
		})
		# no response

	def get_iconpngdata(self, bundleid):
		self._sendmsg({
			u'command': u'getIconPNGData',
			u'bundleId': bundleid
		})
		return self._recvmsg()

	def get_interface_orientation(self):
		self._sendmsg({u'command': u'getInterfaceOrientation'})
		reply = self._recvmsg()
		if reply is None or u'interfaceOrientation' not in reply:
			raise RuntimeError(u'Unable to retrieve interface orientation')
		return reply[u'interfaceOrientation']

	def get_wallpaper_pngdata(self):
		self._sendmsg({
			u'command': u'getHomeScreenWallpaperPNGData',
			u'bundleId': bundleid
		})
		return self._recvmsg()


if __name__ == u'__main__':
	import pprint
	def factory(dev):
		d = AMDevice(dev)
		d.connect()
		sb = Springboard(d)

		#pprint.pprint(sb.get_iconstate())
		#pprint.pprint(sb.get_iconpngdata(u'com.apple.mobilephone'))
		print sb.get_interface_orientation()

		sb.disconnect()
		return d
	
	handle_devices(factory)

