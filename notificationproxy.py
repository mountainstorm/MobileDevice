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


# collect valid notification names e.g.: com.apple.springboard.hasBlankedScreen
class NotificationProxy(PlistService):
	def __init__(self, amdevice):
		PlistService.__init__(
			self, 
			amdevice, 
			[u'com.apple.mobile.notification_proxy']
		)

	def post_notificaiton(self, name):
		self._sendmsg({
			u'Command': u'PostNotification',
			u'Name': name
		})

	def shutdown(self):
		self._sendmsg({
			u'Command': u'Shutdown'
		})
		self._recvmsg() # discard reply

	def register_notification(self, name):
		self._sendmsg({
			u'Command': u'ObserveNotification',
			u'Name': name
		})
	
	def observe_notifications(self):
		msg = None
		while True:
			msg = self._recvmsg()
			if msg is None:
				break
			if u'Command' in msg and msg[u'Command'] == u'RelayNotification':
				msg = msg[u'Name']
				break
			print(u'Unknown message: ' + msg.__str__())
		return msg


def register_argparse_notifyproxy(cmdargs):
	import argparse

	def cmd_post(args, dev):
		notify = NotificationProxy(dev)
		notify.post_notificaiton(args.name.decode(u'utf-8'))
		notify.disconnect()

	def cmd_shutdown(args, dev):
		notify = NotificationProxy(dev)
		notify.shutdown()
		notify.disconnect()

	def cmd_observe(args, dev):
		notify = NotificationProxy(dev)
		notify.register_notification(args.name.decode(u'utf-8'))
		try:
			while True:
				msg = notify.observe_notifications()
				if msg is None:
					break
				print(msg)
		except:
			pass
		notify.disconnect()

	notifyparser = cmdargs.add_parser(
		u'notify',
		help=u'notification proxy commands'
	)
	notifycmds = notifyparser.add_subparsers()

	# post command
	postcmd = notifycmds.add_parser(
		u'post', 
		help=u'post a notification to the system'
	)
	postcmd.add_argument(
		u'name',
		help=u'the name of the notification to send'
	)
	postcmd.set_defaults(func=cmd_post)

	# shutdown command
	shutdowncmd = notifycmds.add_parser(
		u'shutdown', 
		help=u'shutdown the notification system'
	)
	shutdowncmd.set_defaults(func=cmd_shutdown)

	# observe command
	observecmd = notifycmds.add_parser(
		u'observe', 
		help=u'observe a notification in the system'
	)
	observecmd.add_argument(
		u'name',
		help=u'the name of the notification to observe'
	)
	observecmd.set_defaults(func=cmd_observe)



