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


class InstallationProxy(PlistService):
	def __init__(self, amdevice):
		PlistService.__init__(
			self, 
			amdevice, 
			[AMSVC_INSTALLATION_PROXY], 
			kCFPropertyListXMLFormat_v1_0
		)

	def listapplications(self):
		retval = []
		self._sendmsg({
			u'Command': u'Browse',
			u'ClientOptions': {
				u'ApplicationType': u'Any'
			}
		})
		while True:
			reply = self._recvmsg()
			if (    reply is None 
				or (    u'Status' in reply 
					and reply[u'Status'] == u'Complete')):
				break # done
			retval.append(reply[u'CurrentList'])
		return retval

	# TODO: install, upgrade, archive, restore, etc


if __name__ == u'__main__':
	import pprint
	def factory(dev):
		d = AMDevice(dev)
		d.connect()
		ip = InstallationProxy(d)

		pprint.pprint(ip.listapplications())

		ip.disconnect()
		return d
	
	handle_devices(factory)

