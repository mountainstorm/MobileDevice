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
from ctypes import *
from posixpath import *
import stat
import os


def _stat_from_afcdict(afcdict):
	class AFCLStat(object):
		pass

	retval = AFCLStat()
	name = c_char_p()
	value = c_char_p()
	while AFCKeyValueRead(afcdict, byref(name), byref(value)) == MDERR_OK:
		if name.value is None or value.value is None: 
			break

		strname = name.value.decode(u'utf-8')
		if strname == u'st_ifmt':
			modes = {
				u'S_IFSOCK': stat.S_IFSOCK,
				u'S_IFLNK': stat.S_IFLNK,
				u'S_IFREG': stat.S_IFREG,
				u'S_IFBLK': stat.S_IFBLK,
				u'S_IFDIR': stat.S_IFDIR,
				u'S_IFCHR': stat.S_IFCHR,
				u'S_IFIFO': stat.S_IFIFO
			}
			v = value.value.decode(u'utf-8')
			if v not in modes:
				raise RuntimeError(u'Unknown file type:', v)
			setattr(
				retval, 
				strname,
				modes[v]
			)
		elif strname == u'st_mtime' or strname == u'st_birthtime':
			setattr(
				retval, 
				strname, 
				value.value.decode(u'utf-8')[:10]
			)
		else:
			setattr(
				retval, 
				strname, 
				value.value.decode(u'utf-8')
			)
	return retval


class AFCFile(object):
	# XXX creation, read, write, seek tell etc
	def __init__(self, afc_con, path, mode):
		self.afc_con = afc_con
		self.mode = 0
		if mode.find(u'r') != -1:
			self.mode |= 0x1
		if mode.find(u'w') != -1:
			self.mode |= 0x2 
		self.f = AFCFileRef()
		self.closed = True
		if AFCFileRefOpen(
				self.afc_con, 
				path.encode(u'utf-8'), 
				self.mode, 
				byref(self.f)) != MDERR_OK:
			raise IOError(u'Unable to open file:', path, mode)
		self.closed = False

	def __del__(self):
		self.close()

	def close(self):
		if not self.closed:
			AFCFileRefClose(self.afc_con, self.f)
			self.closed = True

	def flush(self):
		pass

	def readable(self):
		return self.mode & 0x1

	def readline(self, limit=-1):
		raise NotImplementedError()

	def readlines(self, limit=-1):
		raise NotImplementedError()

	def seek(self, offset, whence=os.SEEK_SET):
		if AFCFileRefSeek(
				self.afc_con, 
				self.f, offset, 
				whence,
				byref(idx), 0) != MDERR_OK:
			raise ValueError(u'Unable to set file location')

	def seekable(self):
		return True

	def tell(self):
		idx = CFIndex()
		if AFCFileRefTell(self.afc_con, self.f, byref(idx)) != MDERR_OK:
			raise ValueError(u'Unable to read file location')
		return idx.value

	def truncate(size=None):
		if size is None:
			size = self.tell()
		if AFCFileRefSetFileSize(self.afc_con, self.f, size) != MDERR_OK:
			raise ValueError(u'Unable to truncate file')

	def writable(self):
		return self.mode & 0x2

	def writelines(self, lines):
		raise NotImplementedError()

	def lock(self):
		if AFCFileRefLock(self.afc_con, self.f) != MDERR_OK:
			raise ValueError(u'Unable to lock file')

	def unlock(self):
		if AFCFileRefUnlock(self.afc_con, self.f) != MDERR_OK:
			raise ValueError(u'Unable to unlock file')

	def read(self, n=-1):
		retval = ''
		br = 0
		buflen = c_uint32(4096)
		buf = (c_char * buflen.value)()
		while br < n or n == -1:
			buflen.value = 4096
			if AFCFileRefRead(
				self.afc_con, 
				self.f, 
				buf,
				byref(buflen)
			) != MDERR_OK or buflen.value == 0:
				break # eof
			retval += buf.raw[:buflen.value]
			br += buflen.value
		return retval

	def readall(self):
		return self.read()

	def readinto(self, b):
		raise NotImplementedError()

	def write(self, b):
		buflen = c_uint32(len(b))
		buf = c_char_p(b)
		if AFCFileRefWrite(
			self.afc_con,
			self.f,
			buf,
			buflen
		) != MDERR_OK:
			raise RuntimeError(u'Error during write')


class AFC(object):
	def __init__(self, s):
		self.s = s
		self.afc_con = AFCConnectionRef()
		if AFCConnectionOpen(self.s, 0, byref(self.afc_con)) != MDERR_OK:
			raise RuntimeError(u'Unable to open AFC connection')

	def disconnect(self):
		AFCConnectionClose(self.afc_con)

	def link(self, target, link_name):
		if AFCLinkPath(
				self.afc_con, 
				1, # hard
				target.encode(u'utf-8'),
				link_name.encode(u'utf-8')
			) != MDERR_OK:
			raise OSError(u'Unable to create hard link:', target, link_name)
		return True

	# typically you get a class with the following members
	# st_mtime, st_blocks, st_nlink, st_birthtime, st_ifmt, st_size
	def lstat(self, path):
		info = AFCDictionaryRef()
		if AFCFileInfoOpen(
				self.afc_con, 
				path.encode(u'utf-8'), 
				byref(info)
			) != MDERR_OK:
			raise OSError(u'Unable to open path:', path)
		retval = _stat_from_afcdict(info)
		AFCKeyValueClose(info)
		return retval

	def listdir(self, path):
		afc_dir = AFCDirectoryRef()
		if AFCDirectoryOpen(
				self.afc_con, 
				path.encode(u'utf-8'),
				byref(afc_dir)
			) != MDERR_OK:
			raise OSError(u'Unable to open AFC directory:', path)

		retval = []
		name = c_char_p()
		while AFCDirectoryRead(self.afc_con, afc_dir, byref(name)) == MDERR_OK:
			if name.value is None:
				break
			path = name.value.decode(u'utf-8')
			if path != u'.' and path != u'..':
				retval.append(path)
		# XXX do we need to free buffer on error
		AFCDirectoryClose(self.afc_con, afc_dir)
		return retval

	def mkdir(self, path):
		if AFCDirectoryCreate(self.afc_con, path) != MDERR_OK:
			raise OSError(u'Unable to create directory:', path)

	def makedirs(self, path):
		raise NotImplementedError()

	def readlink(self, path):
		s = self.lstat(path)
		if not hasattr(s, u'LinkTarget'):
			raise OSError(u'Path is not symlink:', path)
		return s.LinkTarget

	def remove(self, path):
		return self.unlink(path)

	def removedirs(self, path):
		raise NotImplementedError() 

	def rename(self, src, dst):
		if AFCRenamePath(
				self.afc_con, 
				src.encode(u'utf-8'), 
				dst.encode(u'utf-8')
			) != MDERR_OK:
			raise OSError(u'Unable to rename file:', src, dst)

	def renames(self, old, new):
		raise NotImplementedError()

	def rmdir(self, path):
		return self.unlink(path)

	def stat(self, path):
		retval = self.lstat(path)
		if hasattr(retval, u'LinkTarget'):
			# its a symlink - so stat the link target
			retval = self.lstat(retval.LinkTarget)
		return retval

	def symlink(self, target, link_name):
		if AFCLinkPath(
				self.afc_con, 
				2, # soft 
				target.encode(u'utf-8'),
				link_name.encode(u'utf-8')
			) != MDERR_OK:
			raise OSError(u'Unable to create symlink:', target, link_name)
		return True

	def unlink(self, path):
		if AFCRemovePath(self.afc_con, path.encode(u'utf-8')) != MDERR_OK:
			raise OSError(u'Unable to remove file:', path)

	def open(self, path, mode):
		return AFCFile(self.afc_con, path, mode)


