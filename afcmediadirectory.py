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
from afc import *


class AFCMediaDirectory(AFC):
	def __init__(self, amdevice):
		s = amdevice.start_service(AMSVC_AFC)
		if s is None:
			raise RuntimeError(u'Unable to launch:', AMSVC_AFC)
		AFC.__init__(self, s)

	def transfer_application(self, path, progress=None):
		u'''Transfers an application bundle to the device; into the 
		/PublicStaging directory

		Arguments:
		path -- the local path to the file to transfer
		progress -- the callback to get notified of the transfer process
		            (defaults to none)

		Error:
		Raises RuntimeError on error
		'''
		# Technically you could use this on any AFC connection but it only makes
		# sense to use it on the MediaDirectory - as it hard coded moves stuff 
		# to /PublicStaging
		def callback(cfdict, arg):
			pass

		cfpath = CFTypeFrom(path)
		cb = AFCProgressCallback(callback)
		if progress is not None:
			cb = AFCProgressCallback(progress)
		err = AMDeviceTransferApplication(self.s, cfpath, None, cb, None)
		CFRelease(cfpath)
		if err != MDERR_OK:
			raise RuntimeError(u'Unable to transfer application')


def register_argparse_afc(cmdargs):
	import argparse
	import sys
	import afcapplicationdirectory
	import afccrashlogdirectory
	import afcmediadirectory
	import afcroot
	import time
	import posixpath

	def printdir(afc, path, recurse):
		dirlist = []
		rows = []
		colmax = [0, 0, 0, 0]
		print "afc: ", path
		for name in afc.listdir(path):
			isdir = u''
			info = afc.lstat(posixpath.join(path, name))
			if info.st_ifmt == stat.S_IFDIR:
				isdir = u'/'
				dirlist.append(posixpath.join(path, name))

			types = {
				stat.S_IFSOCK: u's',
				stat.S_IFLNK: u'l',
				stat.S_IFREG: u'-',
				stat.S_IFBLK: u'b',
				stat.S_IFDIR: u'd',
				stat.S_IFCHR: u'c',
				stat.S_IFIFO: u'p'
			}
			modtime = long(info.st_mtime)
			if long(time.time()) - modtime > (60*60*24*365):
				# only show year if its over a year old (ls style)
				strtime = time.strftime(u'%d %b  %Y', time.gmtime(modtime))
			else:
				strtime = time.strftime(u'%d %b %H:%M', time.gmtime(modtime))
			islink = u''
			if info.st_ifmt == stat.S_IFLNK:
				islink = u' -> ' + afc.readlink(posixpath.join(path, name))

			row = (
				types[info.st_ifmt],
				info.st_size,
				strtime,
				name + isdir + islink
			)
			rows.append(row)
			for i in range(len(row)):
				if len(row[i]) > colmax[i]:
					colmax[i] = len(row[i])
	
		for row in rows:
			print(
				row[0].ljust(colmax[0]) + u'  ' +
				row[1].rjust(colmax[1]) + u'  ' + 
				row[2].ljust(colmax[2]) + u'  ' + 
				row[3])

		if recurse:
			for name in dirlist:
				print(u'\n' + name)
				printdir(afc, name, recurse)

	def get_afc(args, dev):
		retval = None
		if args.path.startswith(u'/var/mobile/Media'):
			retval = afcmediadirectory.AFCMediaDirectory(dev)
			args.path = args.path[len(u'/var/mobile/Media'):]
		elif args.m:
			retval = afcmediadirectory.AFCMediaDirectory(dev)
		elif args.c:
			retval = afccrashlogdirectory.AFCCrashLogDirectory(dev)
		elif args.app is not None:
			retval = afcapplicationdirectory.AFCApplicationDirectory(
				dev, 
				args.app.decode(u'utf-8')
			)
		else:
			retval = afcroot.AFCRoot(dev)
		return retval

	def cmd_ls(args, dev):
		afc = get_afc(args, dev)
		printdir(afc, args.path.decode(u'utf-8'), args.r)
		afc.disconnect()

	def cmd_mkdir(args, dev):
		afc = get_afc(args, dev)
		afc.mkdir(args.path)
		afc.disconnect()

	def cmd_rm(args, dev):
		afc = get_afc(args, dev)
		afc.remove(args.path)
		afc.disconnect()

	def cmd_ln(args, dev):
		# XXX unable to make linking work?
		afc = get_afc(args, dev)
		# if we're using the default mediadirectory then adjust the link
		if args.link.startswith(u'/var/mobile/Media'):
			args.link = args.link[len(u'/var/mobile/Media'):]
		if args.s:
			afc.symlink(args.path, args.link)
		else:
			afc.link(args.path, args.link)
		afc.disconnect()

	def cmd_get(args, dev):
		dest = args.dest
		if dest[-1] == os.sep:
			# trailing seperator so dest has same name as src
			dest = posixpath.join(dest, posixpath.basename(args.path))

		afc = get_afc(args, dev)
		s = afc.open(args.path, u'r')
		d = open(dest, u'w+')
		d.write(s.readall())
		d.close()
		s.close()
		afc.disconnect()

	def cmd_put(args, dev):
		if args.path[-1] == os.sep:
			# trailing seperator so dest has same name as src
			args.path = posixpath.join(args.path, posixpath.basename(args.src))

		afc = get_afc(args, dev)
		d = afc.open(args.path, u'w')
		s = open(args.src, u'r')
		d.write(s.read())
		s.close()
		d.close()
		afc.disconnect()

	def cmd_view(args, dev):
		afc = get_afc(args, dev)
		s = afc.open(args.path, u'r')
		d = s.readall()
		s.close()
		afc.disconnect()		
		print(d)

	# afc command
	afcparser = cmdargs.add_parser(
		u'afc', 
		help=u'commands to manipulate files via afc'
	)
	afcgroup = afcparser.add_mutually_exclusive_group()
	afcgroup.add_argument(
		u'-a',
		metavar=u'app',
		dest=u'app',
		help=u'reverse domain name of application; device paths become relative to app container'
	)
	afcgroup.add_argument(
		u'-c',
		action=u'store_true',
		help=u'crashlogs; device paths become relative to crash log container'
	)
	afcgroup.add_argument(
		u'-m',
		action=u'store_true',
		help=u'device paths become relative to /var/mobile/media (saves typing)'
	)
	afccmd = afcparser.add_subparsers()

	# ls command
	lscmd = afccmd.add_parser(
		u'ls',
		help=u'lists the contents of the directory'
	)
	lscmd.add_argument(
		u'-r',
		action=u'store_true',
		help=u'if specified listing is recursive'
	)
	lscmd.add_argument(
		u'path',
		help=u'path on the device to list'
	)
	lscmd.set_defaults(func=cmd_ls)

	# mkdir command
	mkdircmd = afccmd.add_parser(
		u'mkdir',
		help=u'creates a directory'
	)
	mkdircmd.add_argument(
		u'path',
		help=u'path of the dir to create'
	)
	mkdircmd.set_defaults(func=cmd_mkdir)

	# rmdir / rm
	rmcmd = afccmd.add_parser(
		u'rm',
		help=u'remove directory/file'
	)
	rmcmd.add_argument(
		u'path',
		help=u'the path to delete'
	)
	rmcmd.set_defaults(func=cmd_rm)

	rmdircmd = afccmd.add_parser(
		u'rmdir',
		help=u'remove directory/file'
	)
	rmdircmd.add_argument(
		u'path',
		help=u'the path to delete'
	)
	rmdircmd.set_defaults(func=cmd_rm)

	# ln
	lncmd = afccmd.add_parser(
		u'ln',
		help=u'create a link (symbolic or hard)'
	)
	lncmd.add_argument(
		u'path',
		help=u'the pre-existing path to link to'
	)
	lncmd.add_argument(
		u'link',
		help=u'the path for the link'
	)
	lncmd.add_argument(
		u'-s',
		action=u'store_true',
		help=u'create a symbolic link'
	)
	lncmd.set_defaults(func=cmd_ln)

	# get
	getcmd = afccmd.add_parser(
		u'get',
		help=u'retrieve a file from the device'
	)
	getcmd.add_argument(
		u'path',
		help=u'path on the device to retrieve'
	)
	getcmd.add_argument(
		u'dest',
		help=u'local path to write file to'
	)
	getcmd.set_defaults(func=cmd_get)

	# put
	putcmd = afccmd.add_parser(
		u'put',
		help=u'upload a file from the device'
	)
	putcmd.add_argument(
		u'src',
		help=u'local path to read file from'
	)
	putcmd.add_argument(
		u'path',
		help=u'path on the device to write'
	)
	putcmd.set_defaults(func=cmd_put)

	# view
	viewcmd = afccmd.add_parser(
		u'view',
		help=u'retrieve a file from the device and preview as txt'
	)
	viewcmd.add_argument(
		u'path',
		help=u'path on the device to retrieve'
	)
	viewcmd.set_defaults(func=cmd_view)

