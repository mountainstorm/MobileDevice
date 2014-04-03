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
from plistservice import *


class WIRService(PlistService):
	def __init__(self, amdevice, servicenames, format=kCFPropertyListBinaryFormat_v1_0):
		PlistService.__init__(self, amdevice, servicenames, format)

	def _sendmsg(self, selector, args):
		wi = dict_to_plist_encoding({
			u'__selector': selector,
			u'__argument': args
		})
		step = 8096 # split very big messages
		start = 0
		end = step
		while end < len(wi):
			PlistService._sendmsg(self, {
				u'WIRPartialMessageKey': wi[start:end]
			})
			start = end
			end += step
		PlistService._sendmsg(self, {
			u'WIRFinalMessageKey': wi[start:end]
		})

	def _recvmsg(self):
		wi = ''
		wimsg = PlistService._recvmsg(self)
		while wimsg and u'WIRPartialMessageKey' in wimsg:
			wi += wimsg[u'WIRPartialMessageKey']
			wimsg = PlistService._recvmsg(self)
		wi += wimsg[u'WIRFinalMessageKey']
		rpc = dict_from_plist_encoding(wi)
		return (rpc[u'__selector'], rpc[u'__argument'])


