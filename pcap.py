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
from ctypes import *
from datetime import datetime
import socket


class iptap_hdr_t(BigEndianStructure):
	_pack_ = 1
	_fields_ = [
		(u'hdr_length', c_uint32),
		(u'version', c_uint8),
		(u'length', c_uint32),
		(u'type', c_uint8),
		(u'unit', c_uint16),
		(u'io', c_uint8),
		(u'protocol_family', c_uint32),
		(u'frame_pre_length', c_uint32),
		(u'frame_pst_length', c_uint32),
		(u'if_name', c_char * 16)
	]


class Pcap(PlistService):
	def __init__(self, amdevice):
		PlistService.__init__(self, amdevice, [u'com.apple.pcapd'])

	def get_packet(self):
		return self._recvmsg()


class pcap_hdr_t(Structure):
	_pack_ = 1
	_fields_ = [
		(u'magic_number', c_uint32),
		(u'version_major', c_uint16),
		(u'version_minor', c_uint16),
		(u'thiszone', c_int32),
		(u'sigfigs', c_uint32),
		(u'snaplen', c_uint32),
		(u'network', c_uint32)
	]


class pcaprec_hdr_t(Structure):
	_pack_ = 1
	_fields_ = [
		(u'ts_sec', c_uint32),
		(u'ts_usec', c_uint32),
		(u'incl_len', c_uint32),
		(u'orig_len', c_uint32)
	]


class PcapFile(object):

	PCAP_MAGIC = 0xa1b2c3d4
	PCAP_MAJOR_VERSION = 2
	PCAP_MINOR_VERSION = 4

	def __init__(self, filename):
		self._f = open(filename, u'wb')
		# write the hdr
		self._f.write(pcap_hdr_t(
			PcapFile.PCAP_MAGIC,
			PcapFile.PCAP_MAJOR_VERSION,
			PcapFile.PCAP_MINOR_VERSION,
			0,
			0,
			65535, # XXX update this if we ever get a bigger packet
			1 # LINKTYPE_ETHERNET -- data is raw ethernet packets
		))

	def __del__(self):
		self.close()

	def close(self):
		self._f.close()

	def write_packet(self, packetdata):
		now = datetime.now()
		self._f.write(pcaprec_hdr_t(
			now.second,
			now.microsecond,
			len(packetdata),
			len(packetdata)
		))
		self._f.write(packetdata)


def register_argparse_pcap(cmdargs):
	import argparse

	def cmd_pcap(args, dev):
		pcapd = Pcap(dev)
		pcap = PcapFile(args.path.decode(u'utf-8'))
		try:
			while True:
				pkt = pcapd.get_packet()

				hdr = iptap_hdr_t.from_buffer_copy(pkt)
				# wireshark doesn't have support for this protocol so dump iptap hdr
				pcap.write_packet(pkt[sizeof(iptap_hdr_t):])
		except:
			pass
		pcap.close()
		pcapd.disconnect()

	pcapcmd = cmdargs.add_parser(
		u'pcap', 
		help=u'record packets from device into pcap file'
	)
	pcapcmd.add_argument(
		u'path',
		help=u'path of the file to write'
	)
	pcapcmd.set_defaults(func=cmd_pcap)

