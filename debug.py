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
from installationproxy import *
import os
import tempfile
import posixpath


class DebugServer(object):
	u'''Debugserver class; starts an instance of debugserver and spawns an lldb
	instance to talk to it'''

	def __init__(self, amdevice):
		self.s = amdevice.start_service(u'com.apple.debugserver')
		if self.s is None:
			raise RuntimeError(u'Unable to launch:', u'com.apple.debugserver')

	def disconnect(self):
		os.close(self.s)


class DebugAppList(object):
	u'''Debugserver class; starts an instance of debugserver and spawns an lldb
	instance to talk to it'''

	def __init__(self, amdevice):
		self.s = amdevice.start_service(u'com.apple.debugserver.applist')
		if self.s is None:
			raise RuntimeError(u'Unable to launch:', u'com.apple.debugserver.applist')

	def get_applist(self):
		u'''Retrieves an list of aplications on the device; with pids if their 
		running

		Returns:
		An array of dict's (pid is optional) e.g.
			<key>displayName</key>
			<string>Phone</string>
			<key>executablePath</key>
			<string>/Applications/MobilePhone.app/MobilePhone</string>
			<key>isFrontApp</key>
			<false/>
			<key>pid</key>
			<integer>87</integer>
		'''
		retval = ''
		os.write(self.s, u'ping') # XXX we need to prod it somehow
		while True:
			data = os.read(self.s, 4096)
			if len(data) == 0:
				break
			retval += data
		return dict_from_plist_encoding(retval, kCFPropertyListXMLFormat_v1_0)

	def disconnect(self):
		os.close(self.s)


class GDB(object):
	def __init__(self, dev, device_support_path, local_path, remote_path=None):
		self.dev = dev
		self._file = None
		self._substitutions = []
		self._runcmds = u''

		if device_support_path is None:
			device_support_path = dev.find_device_support_path()		

		self._set_file(local_path, remote_path)
		# add standard substitutions
		root = os.path.join(device_support_path, u'Symbols')
		for f in os.listdir(root):
			if os.path.isdir(os.path.join(root, f)):
				self._add_substitution(
					u'/' + f, 
					posixpath.join(root, f)
				)

	def find_gdb(self):
		return u'/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/libexec/gdb/gdb-arm-apple-darwin'

	def _set_debugserver_fd(self, fd):
		# now gdb's remote protocol requires us to setup a unix socket; when you
		# specify 'target remote-mobile <unix socket path>' it then opens this
		# and reads a control message; containing the fd to use to actually 
		# talk to the debugserver.  It then tkes this and does a standard 
		# 'target remote-OSX filedesc:<fd>' command.
		#
		# As I'm lazy I'm just going to pass it the fd directly		
		self._debugserver_fd = fd

	def _get_bundleid(self, local_path):
		# open the app and get its id
		f = open(os.path.join(local_path, u'Info.plist'), u'rb')
		plist = f.read()
		f.close()
		info = dict_from_plist_encoding(plist)
		return info[u'CFBundleIdentifier']

	def _set_file(self, local_path, remote_path=None):
		import pprint 

		if remote_path is None:
			# we dont know where its gone; this should only apply for 
			# non-jailbroken devices i.e. where you can only debug apps
			# thus we can get the local appid, then lookup where on the device 
			# it is ... simples
			bundleid = self._get_bundleid(local_path)

			ip = InstallationProxy(self.dev)
			apps = ip.lookup_applications()
			ip.disconnect()
			#pprint.pprint(apps)
			for app in apps:
				if app[u'CFBundleIdentifier'] == bundleid:
					remote_path = app[u'Path']
					break
			if remote_path is None:
				raise RuntimeError(
					u'Application %s, not installed on device' % bundleid
				)
		else:
			# we want the remote path to be the directory; for a .app thats 
			# not a problem - but for a native macho we need adjust
			remote_path = posixpath.split(remote_path)[0]
		self._file = (local_path, remote_path)

		# we also want to add a substitution for our enclosing folder
		if local_path[-1] == u'/' or local_path[-1] == u'\\':
			local_path = local_path[:-1]
		local_folder = os.path.dirname(local_path)

		if remote_path[-1] == u'/' or remote_path[-1] == u'\\':
			remote_path = remote_path[:-1]
		remote_folder = posixpath.dirname(remote_path)
		self._add_substitution(local_folder, remote_folder)

	def _add_substitution(self, local_folder, remote_folder):
		self._substitutions.append((local_folder, remote_folder))		
		# we can get errors if the remote folder is in /private/var - its 
		# normally refered to by /var.  So add another substitution if need be.
		# there may be other cases of this but this it the only one I've seen
		if remote_folder.startswith(u'/private/var'):
			remote_folder = remote_folder.replace(u'/private/var', u'/var/')
			self._substitutions.append((local_folder, remote_folder))

	def _get_initial_cmds(self):
		retval = u'''
set auto-raise-load-levels 1
set mi-show-protections off
set trust-readonly-sections 1
set inferior-auto-start-dyld 0
set minimal-signal-handling 1

set env NSUnbufferedIO YES

set sharedlibrary check-uuids on
set sharedlibrary load-rules \\".*\\" \\".*\\" container

set shlib-path-substitutions'''
	
		# add all the path substitutions
		for s in self._substitutions:
			retval += u' "%s" "%s"' % s

		retval += u'''
set remote max-packet-size 4096
set remote executable-directory %s
set remote noack-mode 1
target remote-macosx filedesc: %u

mem 0x1000 0x3fffffff cache
mem 0x40000000 0xffffffff none
mem 0x00000000 0x0fff none
''' % (self._file[1], self._debugserver_fd)

		retval += self._runcmds

		retval += u'''
set minimal-signal-handling 0
set inferior-auto-start-cfm off
set sharedLibrary load-rules dyld ".*libobjc.*" all dyld ".*CoreFoundation.*" all dyld ".*Foundation.*" all dyld ".*libSystem.*" all dyld ".*AppKit.*" all dyld ".*PBGDBIntrospectionSupport.*" all dyld ".*/usr/lib/dyld.*" all dyld ".*CarbonDataFormatters.*" all dyld ".*libauto.*" all dyld ".*CFDataFormatters.*" all dyld "/System/Library/Frameworks\\\\\\\\|/System/Library/PrivateFrameworks\\\\\\\\|/usr/lib" extern dyld ".*" all exec ".*" all
sharedlibrary apply-load-rules all
set inferior-auto-start-dyld 1
'''
		#print(retval)
		return retval

	def set_run(self, args=None):
		# we specify file when running; we can't when doing attach
		runcmd = u'file "%s"\nrun' % (self._file[0])
		if args is not None:
			for arg in args:
				runcmd += u'"%s"' % arg
		runcmd += u'\n'
		self._runcmds = runcmd

	def set_attach(self, pid):
		# XXX figure out what we should use instead of file - perhaps exec-file?
		self._runcmds = u'attach %s' % pid

	def run(self):
		# create the temp file and fill it with the init commands
		cmdfd, path = tempfile.mkstemp()

		# start debug server
		dbg = DebugServer(self.dev)
		self._set_debugserver_fd(dbg.s)

		os.write(cmdfd, self._get_initial_cmds())
		os.close(cmdfd)

		# start gdb
		os.system(self.find_gdb() + u' --arch armv7 -q -x "%s"' % path)

		# cleanup
		dbg.disconnect()
		os.unlink(path)


def register_argparse_debugserver(cmdargs):
	import argparse
	import sys
	import imagemounter

	def load_developer_dmg(args, dev):
		if not args.advanced:
			# we only load in non-advanced mode
			try:
				# we're doing this as, for some reason, the checking load image
				# does isn;t very good - so if we don;t we end up transfering 
				# the image every time; which is slow and generates tonnes of 
				# log messages
				applist = DebugAppList(dev)
				applist.disconnect()
				# it's already loaded
			except:
				# its not ... so find and load the disk image
				im = imagemounter.ImageMounter(dev)
				imagepath = None
				if args.device_support_path:
					imagepath = dev.find_developer_disk_image_path(
						args.device_support_path.decode(u'utf-8')
					)
				im.mount(imagepath)
				im.disconnect()

	def cmd_applist(args, dev):
		load_developer_dmg(args, dev)

		applist = DebugAppList(dev)
		al = applist.get_applist()
		applist.disconnect()

		rows = []
		colmax = [0, 0, 0]
		for app in al:
			# pid
			pid = u'-'
			try:
				# XXX why does hasattr not work properly on this?
				pid = u'%u' % app[u'pid']
			except:
				pass
			if len(pid) > colmax[0]:
				colmax[0] = len(pid)

			# foreground
			foreground = u' '
			if app[u'isFrontApp']:
				foreground = u'*'

			# name
			name = app[u'displayName']
			if len(name) > colmax[1]:
				colmax[1] = len(name)

			# path
			path = app[u'executablePath']
			if len(path) > colmax[2]:
				colmax[2] = len(path)
			rows.append([pid, foreground, name, path])

		for row in rows:
			print(
				row[0].rjust(colmax[0]) + u' ' +
				row[1] + u' ' +
				row[2].ljust(colmax[1]) + u'  ' + 
				row[3].ljust(colmax[2])
			)

	def cmd_gdb(args, dev):
		load_developer_dmg(args, dev)

		remote = None
		if args.remote is not None:
			remote = args.remote.decode(u'utf-8')
		gdb = GDB(
			dev, 
			args.device_support_path.decode(u'utf-8'), 
			args.program.decode(u'utf-8'),
			remote
		)
		if args.p:
			gdb.set_attach(int(args.p)) # attach
		else:
			gdb.set_run() # spawn
		gdb.run()

	debugparser = cmdargs.add_parser(
		u'debug', 
		help=u'debugging commands; utilising debugserver in the developer .dmg'
	)
	debugparser.add_argument(
		u'-s',
		metavar=u'support-path',
		dest=u'device_support_path',
		help=u'specify a custom device support folder; instead of finding the default'
	)
	debugcmd = debugparser.add_subparsers()

	# applist command
	applistcmd = debugcmd.add_parser(
		u'applist',
		help=u'lists applications; which is front and pid if running'
	)
	applistcmd.set_defaults(func=cmd_applist)

	# gdb command
	gdbcmd = debugcmd.add_parser(
		u'gdb', 
		help=u'launches gdb; connected to the device'
	)
	gdbcmd.add_argument(
		u'-p',
		metavar=u'pid',
		help=u'if specified we attempt to connect to this process rather than start a new instance'
	)
	gdbcmd.add_argument(
		u'program', 
		help=u'local path to the program to debug; the file must already be on the device'
	)
	gdbcmd.add_argument(
		u'remote', 
		nargs=u'?',
		help=u'if the program is a plain mach-o rather than a .app you also need to specify where on the device the file resides'
	)
	gdbcmd.set_defaults(func=cmd_gdb)

