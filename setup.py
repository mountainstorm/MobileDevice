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


from distutils.core import setup
import os.path
import os
from subprocess import check_output


def readfile(filename):
	f = open(filename)
	text = f.read()
	f.close()
	return text

def getcommit():
	retval = u''
	try:
		retval = check_output([u'git', u'rev-list', u'--all', u'--count'])
		retval = u'.' + retval.strip()
	except:
		pass
	return retval


setup(
	name=u'Distutils',
	version=u'1.0' + getcommit(),
	description=u'A python package, and command line tool, which wraps Apple\'s MobileDevice API - providing access to iOS devices',
	long_description = readfile(u'README.md'),
	author=u'Cooper',
	url=u'https://github.com/mountainstorm/MobileDevice',
	classifiers = [
		u'Development Status :: 5 - Production/Stable',
		u'Environment :: Console',
		u'Environment :: MacOS X',
		u'Intended Audience :: Developers',
		u'License :: OSI Approved :: MIT License',
		u'Natural Language :: English',
		u'Operating System :: MacOS :: MacOS X',
		u'Programming Language :: Python',
		u'Programming Language :: Python :: 2.7',
		u'Topic :: Security',
		u'Topic :: Software Development :: Libraries :: Python Modules',
		u'Topic :: Utilities',
	],
	license= readfile(u'LICENSE'),
	packages=['MobileDevice'],
	package_dir={'': u'../'},
	scripts=[u'mdf']
)
