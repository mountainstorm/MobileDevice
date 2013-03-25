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
import uuid


# Talk to safari using https://developers.google.com/chrome-developer-tools/docs/protocol/1.0/index
class WebKitInspector(PlistService):
	def __init__(self, amdevice):
		PlistService.__init__(self, amdevice, [AMSVC_WEBINSPECTOR])

	def _sendmsg(self, selector, args):
		PlistService._sendmsg(self, {
			u'WIRFinalMessageKey': dict_to_plist_encoding({
				u'__selector': selector,
				u'__argument': args
			})
		})

	def _readmsg(self):
		wi = PlistService._recvmsg(self)
		rpc = dict_from_plist_encoding(wi[u'WIRFinalMessageKey'])
		return (rpc[u'__selector'], rpc[u'__argument'])

	def uniqueid(self):
		retval = str(uuid.uuid1())
		if isinstance(retval, str):
			# get round a bug in safari's implementation of 'forwardSocketSetup'
			# they don't check the type/convert WIRConnectionIdentifierKey
			# Thus if we send a string, it converts to a CFData and Safari goes
			# pop when it tries to call compare on the CFData
			retval = retval.decode(u'utf-8') 
		return retval

	# register a connection_uuid
	def reportIdentifier(self, connection_uuid):
		self._sendmsg(
			u'_rpc_reportIdentifier:',
			{ 
				u'WIRConnectionIdentifierKey': connection_uuid,
			}
		)
		print self._readmsg()
		print self._readmsg()

	# list avaliable applications
	def getConnectedApplications(self, connection_uuid):
		self._sendmsg(
			u'_rpc_getConnectedApplications:',
			{
				u'WIRConnectionIdentifierKey': connection_uuid
			}
		)
		print self._readmsg()

	# get info about an applications e.g. pages in mobilesafari
	def forwardGetListing(self, connection_uuid, appid):
		self._sendmsg(
			u'_rpc_forwardGetListing:',
			{
				u'WIRConnectionIdentifierKey': connection_uuid,
				u'WIRApplicationIdentifierKey': appid
			}
		)
		print self._readmsg()

	# highlight a webview page
	def forwardIndicateWebView(self, connection_uuid, appid, pageid, enable):
		self.sendmsg(
			u'_rpc_forwardIndicateWebView:',
			{
				u'WIRConnectionIdentifierKey': connection_uuid,
				u'WIRApplicationIdentifierKey': appid,
				u'WIRPageIdentifierKey': pageid,
				u'WIRIndicateEnabledKey': enable
			}
		)
		print self._readmsg()

	# setup a webkit protocol connection
	def forwardSocketSetup(self, connection_uuid, appid, pageid, sender_uuid):
		self._sendmsg(
			u'_rpc_forwardSocketSetup:',
			{ 
				u'WIRConnectionIdentifierKey':  connection_uuid,
				u'WIRApplicationIdentifierKey': appid,
				u'WIRPageIdentifierKey': pageid,
				u'WIRSenderKey': sender_uuid
			}
		)
		print self._readmsg()

	# send webkit protocol message
	def forwardSocketData(self, connection_uuid, appid, pageid, sender_uuid, jsonmsg):
		self._sendmsg(
			u'_rpc_forwardSocketData:',
			{ 
				u'WIRConnectionIdentifierKey': connection_uuid,
				u'WIRApplicationIdentifierKey': appid,
				u'WIRPageIdentifierKey': pageid,
				u'WIRSenderKey': sender_uuid,
				u'WIRSocketDataKey': jsonmsg.encode(u'utf-8')
			}
		)
		print self._readmsg()

	def forwardDidClose(self, connection_uuid, appid, pageid, sender_uuid):
		self.sendmsg(
			u'_rpc_forwardDidClose:',
			{ 
				u'WIRConnectionIdentifierKey': connection_uuid,
				u'WIRApplicationIdentifierKey': appid,
				u'WIRPageIdentifierKey': pageid,
				u'WIRSenderKey': sender_uuid
			}
		)
		print self._readmsg()


if __name__ == u'__main__':
	def factory(dev):
		d = AMDevice(dev)
		d.connect()
		wi = WebKitInspector(d)
		c = wi.uniqueid()
		s = wi.uniqueid()
		p = 2
		app = u'com.apple.mobilesafari'
		wi.reportIdentifier(c)
		wi.forwardGetListing(c, app)
		wi.forwardSocketSetup(c, app, p, s)
		wi.forwardSocketData(c, app, p, s, u'{"id": 1, "method": "Page.navigate", "params": {"url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="}}')
		wi.disconnect()
		return d
	
	handle_devices(factory)



		

