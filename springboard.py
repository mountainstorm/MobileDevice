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
import time


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
		self._sendmsg({
			u'command': u'getIconState',
			u'formatVersion': u'2'
		})
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
		return self._recvmsg()[u'pngData']

	def get_interface_orientation(self):
		self._sendmsg({u'command': u'getInterfaceOrientation'})
		reply = self._recvmsg()
		if reply is None or u'interfaceOrientation' not in reply:
			raise RuntimeError(u'Unable to retrieve interface orientation')
		return reply[u'interfaceOrientation']

	def get_wallpaper_pngdata(self):
		self._sendmsg({u'command': u'getHomeScreenWallpaperPNGData'})
		return self._recvmsg()[u'pngData']


def register_argparse_springboard(cmdargs):
	import argparse
	import pprint
	import sys

	def cmd_icon(args, dev):
		sb = Springboard(dev)
		data = sb.get_iconpngdata(args.appid.decode(u'utf-8'))
		sb.disconnect()
		f = open(args.path.decode(u'utf-8'), u'wb')
		f.write(data)
		f.close()

	def cmd_orient(args, dev):
		sb = Springboard(dev)
		orient = sb.get_interface_orientation()
		sb.disconnect()

		orient_str = {
			Springboard.PORTRAIT: u'↑',
			Springboard.PORTRAIT_UPSIDE_DOWN: u'↓',
			Springboard.LANDSCAPE: u'←',
			Springboard.LANDSCAPE_HOME_TO_LEFT: u'→'
		}
		print(orient_str[orient])

	def cmd_wallpaper(args, dev):
		sb = Springboard(dev)
		data = sb.get_wallpaper_pngdata()
		sb.disconnect()
		f = open(args.path.decode(u'utf-8'), u'wb')
		f.write(data)
		f.close()

	def print_icons(state, pad=u''):
		retval = u''
		rows = []
		colmax = [0, 0, 0, 0, 0]
		pageid = 0
		for page in state:
			iconid = 0
			for icon in page:
				displayname = icon[u'displayName']
				pos = u'%u:%u' % (pageid, iconid)
				if len(pos) > colmax[0]:
					colmax[0] = len(pos)				
				bundleid = u''
				version = u''
				modtime = u''
				strtime = u''
				extras = u''
				if u'listType' in icon:
					# its a special type
					displayname += u'/'
					if icon[u'listType'] == u'folder':
						extras = print_icons(icon[u'iconLists'], u'  ')
					elif icon[u'listType'] == u'newsstand':
						extras = print_icons(icon[u'iconLists'], u'  ')
					else:
						raise NotImplementedError(u'unsupported listType', icon)
				else:
					#print icon
					bundleid = icon[u'bundleIdentifier']
					if len(bundleid) > colmax[2]:
						colmax[2] = len(bundleid)
					version = icon[u'bundleVersion']
					if len(version) > colmax[3]:
						colmax[3] = len(version)
					modtime = time.mktime(icon[u'iconModDate'].timetuple()) * 1000
					if long(time.time()) - modtime > (60*60*24*365):
						# only show year if its over a year old (ls style)
						strtime = time.strftime(u'%d %b  %Y', time.gmtime(modtime))
					else:
						strtime = time.strftime(u'%d %b %H:%M', time.gmtime(modtime))
					if len(strtime) > colmax[4]:
						colmax[4] = len(strtime)
				if len(displayname) > colmax[1]:
					colmax[1] = len(displayname)
				rows.append((pos, displayname, bundleid, version, strtime, extras))
				iconid += 1
			pageid += 1
			if pageid != len(state):
				rows.append((u'', u'', u'', u'', u'', u''))

		for row in rows:
			retval += (
				pad + 
				row[0].ljust(colmax[0]) + u'  ' +
				row[1].ljust(colmax[1]) + u'  ' +
				row[4].ljust(colmax[4]) + u'  ' + 
				row[3].rjust(colmax[3]) + u'  ' + 
				row[2].ljust(colmax[2]) + u'\n'
				
			)
			retval += row[5]
		return retval

	def cmd_getstate(args, dev):
		sb = Springboard(dev)
		state = sb.get_iconstate()
		sb.disconnect()	
		print print_icons(state)

	springboardparser = cmdargs.add_parser(
		u'springboard',
		help=u'springboard related controls'
	)
	springboardcmds = springboardparser.add_subparsers()

	# icon command
	iconcmd = springboardcmds.add_parser(
		u'icon',
		help=u'retrieves the icon png data'
	)
	iconcmd.add_argument(
		u'appid',
		help=u'the application bundle id'
	)
	iconcmd.add_argument(
		u'path',
		help=u'the file to write to'
	)
	iconcmd.set_defaults(func=cmd_icon)

	# orient command
	orientcmd = springboardcmds.add_parser(
		u'orient',
		help=u'retrieves the orientation of the foreground app'
	)
	orientcmd.set_defaults(func=cmd_orient)

 	# wallpaper command
	wallpapercmd = springboardcmds.add_parser(
		u'wallpaper',
		help=u'retrieves the wallpaper png data'
	)
	wallpapercmd.add_argument(
		u'path',
		help=u'the file to write to'
	)
	wallpapercmd.set_defaults(func=cmd_wallpaper)

	# get icon state command
	statecmd = springboardcmds.add_parser(
		u'get-state',
		help=u'get the state info for application icons'
	)
	statecmd.set_defaults(func=cmd_getstate)


