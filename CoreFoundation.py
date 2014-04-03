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


from ctypes import *
import platform
import datetime


if platform.system() == u'Darwin':
	CoreFoundation = CDLL(u'/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
elif platform.system() == u'Windows':
	raise NotImplementedError(u'need to find and import the CoreFoundation dll')
else:
	raise OSError(u'Platform not supported')


# Supporting types
CFAllocatorRef = c_void_p
CFOptionFlags = c_ulong
CFTimeInterval = c_double
CFBoolean = c_bool
CFIndex = c_long


# CFType
CFTypeID = c_long
CFTypeRef = c_void_p

CFRelease = CoreFoundation.CFRelease
CFRelease.restype = None
CFRelease.argtypes = [CFTypeRef]

CFRetain = CoreFoundation.CFRetain
CFRetain.restype = None
CFRetain.argtypes = [CFTypeRef]

CFShow = CoreFoundation.CFShow
CFShow.restype = None
CFShow.argtypes = [CFTypeRef]

CFGetTypeID = CoreFoundation.CFGetTypeID
CFGetTypeID.restype = CFTypeID
CFGetTypeID.argtypes = [CFTypeRef]


# CFBoolean
CFBooleanRef = c_void_p

CFBooleanGetTypeID = CoreFoundation.CFBooleanGetTypeID
CFBooleanGetTypeID.restype = CFTypeID
CFBooleanGetTypeID.argtypes = []

CFBooleanGetValue = CoreFoundation.CFBooleanGetValue
CFBooleanGetValue.restype = c_bool
CFBooleanGetValue.argtypes = [CFBooleanRef]

kCFBooleanTrue = c_void_p.in_dll(CoreFoundation, u'kCFBooleanTrue')
kCFBooleanFalse = c_void_p.in_dll(CoreFoundation, u'kCFBooleanFalse')


# CFNumber
CFNumberRef = c_void_p
CFNumberType = c_long

kCFNumberLongType = 10
kCFNumberSInt32Type = 3
kCFNumberDoubleType = 13

CFNumberGetTypeID = CoreFoundation.CFNumberGetTypeID
CFNumberGetTypeID.restype = CFTypeID
CFNumberGetTypeID.argtypes = []

CFNumberCreate = CoreFoundation.CFNumberCreate
CFNumberCreate.restype = CFNumberRef
CFNumberCreate.argtypes = [CFAllocatorRef, CFNumberType, c_void_p]

CFNumberGetType = CoreFoundation.CFNumberGetType
CFNumberGetType.restype = CFNumberType
CFNumberGetType.argtypes = [CFNumberRef]

CFNumberGetValue = CoreFoundation.CFNumberGetValue
CFNumberGetValue.restype = c_bool
CFNumberGetValue.argtypes = [CFNumberRef, CFNumberType, c_void_p]

CFNumberIsFloatType = CoreFoundation.CFNumberIsFloatType
CFNumberIsFloatType.restype = c_bool
CFNumberIsFloatType.argtypes = [CFNumberRef]


# CFString
CFStringRef = c_void_p
CFStringEncoding = c_uint32

kCFStringEncodingUTF8 = 0x08000100
kCFStringEncodingUTF16LE = 0x14000100
kCFStringEncodingUnicode = 0x0100

CFSTR = CoreFoundation.__CFStringMakeConstantString
CFSTR.restype = CFStringRef
CFSTR.argtypes = [c_char_p]

CFStringGetTypeID = CoreFoundation.CFStringGetTypeID
CFStringGetTypeID.restype = CFTypeID
CFStringGetTypeID.argtypes = []

CFStringCreateWithCString = CoreFoundation.CFStringCreateWithCString
CFStringCreateWithCString.restype = CFStringRef
CFStringCreateWithCString.argtypes = [CFAllocatorRef, c_char_p, CFStringEncoding]

CFStringCreateWithBytes = CoreFoundation.CFStringCreateWithBytes
CFStringCreateWithBytes.restype = CFStringRef
CFStringCreateWithBytes.argtypes = [
	CFAllocatorRef,
	POINTER(c_uint8),
	CFIndex,
	CFStringEncoding,
	c_bool
]

CFStringGetMaximumSizeForEncoding = CoreFoundation.CFStringGetMaximumSizeForEncoding
CFStringGetMaximumSizeForEncoding.restype = CFIndex
CFStringGetMaximumSizeForEncoding.argtypes = [CFIndex, CFStringEncoding]

CFStringCreateWithCharacters = CoreFoundation.CFStringCreateWithCharacters
CFStringCreateWithCharacters.restype = CFStringRef
CFStringCreateWithCharacters.argtypes = [CFAllocatorRef, c_wchar_p, CFIndex]

CFStringGetCString = CoreFoundation.CFStringGetCString
CFStringGetCString.restype = CFBoolean
CFStringGetCString.argtypes = [CFStringRef, c_void_p, CFIndex, CFStringEncoding]

CFStringGetLength = CoreFoundation.CFStringGetLength
CFStringGetLength.restype = CFIndex
CFStringGetLength.argtypes = [CFStringRef]

# CFError
CFErrorRef = c_void_p

CFErrorCopyDescription = CoreFoundation.CFErrorCopyDescription
CFErrorCopyDescription.restype = CFStringRef
CFErrorCopyDescription.argtypes = [CFErrorRef]


# CFData
CFDataRef = c_void_p

CFDataGetTypeID = CoreFoundation.CFDataGetTypeID
CFDataGetTypeID.restype = CFTypeID
CFDataGetTypeID.argtypes = []

CFDataCreate = CoreFoundation.CFDataCreate
CFDataCreate.restype = CFDataRef
CFDataCreate.argtypes = [CFAllocatorRef, POINTER(c_uint8), CFIndex]

CFDataCreateWithBytesNoCopy = CoreFoundation.CFDataCreateWithBytesNoCopy
CFDataCreateWithBytesNoCopy.restype = CFDataRef
CFDataCreateWithBytesNoCopy.argtypes = [
	CFAllocatorRef, 
	POINTER(c_uint8),
	CFIndex,
	CFAllocatorRef
]

CFDataGetBytePtr = CoreFoundation.CFDataGetBytePtr
CFDataGetBytePtr.restype = POINTER(c_uint8)
CFDataGetBytePtr.argtypes = [CFDataRef]

CFDataGetLength = CoreFoundation.CFDataGetLength
CFDataGetLength.restype = CFIndex
CFDataGetLength.argtypes = [CFDataRef]


# CFDictionary
CFDictionaryRef = c_void_p

CFDictionaryGetTypeID = CoreFoundation.CFDictionaryGetTypeID
CFDictionaryGetTypeID.restype = CFTypeID
CFDictionaryGetTypeID.argtypes = []

CFDictionaryCreate = CoreFoundation.CFDictionaryCreate
CFDictionaryCreate.restype = CFDictionaryRef
CFDictionaryCreate.argtypes = [
	CFAllocatorRef,
	POINTER(c_void_p),
	POINTER(c_void_p),
	CFIndex,
	POINTER(c_void_p),
	POINTER(c_void_p)
]

CFDictionaryGetCount = CoreFoundation.CFDictionaryGetCount
CFDictionaryGetCount.restype = CFIndex
CFDictionaryGetCount.argtypes = [CFDictionaryRef]

CFDictionaryGetKeysAndValues = CoreFoundation.CFDictionaryGetKeysAndValues
CFDictionaryGetKeysAndValues.restype = None
CFDictionaryGetKeysAndValues.argtypes = [
	CFDictionaryRef, 
	POINTER(c_void_p),
	POINTER(c_void_p)
]

CFDictionaryGetValue = CoreFoundation.CFDictionaryGetValue
CFDictionaryGetValue.restype = CFTypeRef
CFDictionaryGetValue.argtypes = [CFDictionaryRef, CFTypeRef]

kCFTypeDictionaryKeyCallBacks = c_void_p.in_dll(CoreFoundation, u'kCFTypeDictionaryKeyCallBacks')
kCFTypeDictionaryValueCallBacks = c_void_p.in_dll(CoreFoundation, u'kCFTypeDictionaryValueCallBacks')

CFDictionarySetValue = CoreFoundation.CFDictionarySetValue
CFDictionarySetValue.restype = None
CFDictionarySetValue.argtypes = [CFDictionaryRef, CFTypeRef, CFTypeRef]


# CFDate
CFDateRef = c_void_p

CFDateGetTypeID = CoreFoundation.CFDateGetTypeID
CFDateGetTypeID.restype = CFTypeID
CFDateGetTypeID.argtypes = []

CFDateCreate = CoreFoundation.CFDateCreate
CFDateCreate.restype = CFDateRef
CFDateCreate.argtypes = [CFAllocatorRef, c_double]

CFDateGetAbsoluteTime = CoreFoundation.CFDateGetAbsoluteTime
CFDateGetAbsoluteTime.restype = c_double
CFDateGetAbsoluteTime.argtypes = [CFDateRef]


# CFPropertyList
CFPropertyListRef = c_void_p
CFPropertyListFormat = c_long

kCFPropertyListOpenStepFormat = 1
kCFPropertyListXMLFormat_v1_0 = 100
kCFPropertyListBinaryFormat_v1_0 = 200

kCFPropertyListImmutable = 0
kCFPropertyListMutableContainers = 1
kCFPropertyListMutableContainersAndLeaves = 2

CFPropertyListCreateData = CoreFoundation.CFPropertyListCreateData
CFPropertyListCreateData.restype = CFDataRef
CFPropertyListCreateData.argtypes = [
	CFAllocatorRef,
	CFPropertyListRef,
	CFPropertyListFormat,
	CFOptionFlags,
	POINTER(CFErrorRef)
]

CFPropertyListCreateWithData = CoreFoundation.CFPropertyListCreateWithData
CFPropertyListCreateWithData.restype = CFPropertyListRef
CFPropertyListCreateWithData.argtypes = [
	CFAllocatorRef,
	CFDataRef,
	CFOptionFlags,
	POINTER(CFPropertyListFormat),
	POINTER(CFErrorRef)
]

# CFArray
CFArrayRef = c_void_p

CFArrayGetTypeID = CoreFoundation.CFArrayGetTypeID
CFArrayGetTypeID.restype = CFTypeID
CFArrayGetTypeID.argtypes = []

CFArrayGetCount = CoreFoundation.CFArrayGetCount
CFArrayGetCount.restype = CFIndex
CFArrayGetCount.argtypes = [CFArrayRef]

CFArrayGetValueAtIndex = CoreFoundation.CFArrayGetValueAtIndex
CFArrayGetValueAtIndex.restype = c_void_p
CFArrayGetValueAtIndex.argtypes = [CFArrayRef, CFIndex]

CFArrayCreate = CoreFoundation.CFArrayCreate
CFArrayCreate.restype = CFArrayRef
CFArrayCreate.argtypes = [CFAllocatorRef, POINTER(c_void_p), CFIndex, c_void_p]

kCFTypeArrayCallBacks = c_void_p.in_dll(CoreFoundation, u'kCFTypeArrayCallBacks')


# CFRunLoop
CFRunLoopSourceRef = c_void_p
CFRunLoopRef = c_void_p
kCFRunLoopDefaultMode = c_void_p.in_dll(CoreFoundation, u'kCFRunLoopDefaultMode')

kCFRunLoopRunFinished = 1
kCFRunLoopRunStopped = 2
kCFRunLoopRunTimedOut = 3
kCFRunLoopRunHandledSource = 4

CFRunLoopRun = CoreFoundation.CFRunLoopRun
CFRunLoopRun.restype = None
CFRunLoopRun.argtypes = []

CFRunLoopRunInMode = CoreFoundation.CFRunLoopRunInMode
CFRunLoopRunInMode.restype = c_int32
CFRunLoopRunInMode.argtypes = [
	CFStringRef,
	CFTimeInterval,
	c_bool
]

CFRunLoopGetCurrent = CoreFoundation.CFRunLoopGetCurrent
CFRunLoopGetCurrent.restype = CFRunLoopRef
CFRunLoopGetCurrent.argtypes = []

CFRunLoopGetMain = CoreFoundation.CFRunLoopGetMain
CFRunLoopGetMain.restype = CFRunLoopRef
CFRunLoopGetMain.argtypes = []

CFRunLoopStop = CoreFoundation.CFRunLoopStop
CFRunLoopStop.restype = None
CFRunLoopStop.argtypes = [CFRunLoopRef]

# Util/Debug functions
CFCopyDescription = CoreFoundation.CFCopyDescription
CFCopyDescription.restype = CFStringRef
CFCopyDescription.argtypes = [CFTypeRef]

CFCopyTypeIDDescription = CoreFoundation.CFCopyTypeIDDescription
CFCopyTypeIDDescription.restype = CFStringRef
CFCopyTypeIDDescription.argtypes = [CFTypeID]


# CFUUID
CFUUIDRef = c_void_p

CFUUIDGetTypeID = CoreFoundation.CFUUIDGetTypeID
CFUUIDGetTypeID.restype = CFTypeID
CFUUIDGetTypeID.argtypes = []

CFUUIDGetConstantUUIDWithBytes = CoreFoundation.CFUUIDGetConstantUUIDWithBytes
CFUUIDGetConstantUUIDWithBytes.restype = CFUUIDRef
CFUUIDGetConstantUUIDWithBytes.argtypes = [CFAllocatorRef, 
	c_uint8, c_uint8, c_uint8, c_uint8, c_uint8, c_uint8, c_uint8, c_uint8, 
	c_uint8, c_uint8, c_uint8, c_uint8, c_uint8, c_uint8, c_uint8, c_uint8
]

class CFUUIDBytes(Structure):
	_fields_ = [
		(u'byte0', c_uint8),
		(u'byte1', c_uint8),
		(u'byte2', c_uint8),
		(u'byte3', c_uint8),
		(u'byte4', c_uint8),
		(u'byte5', c_uint8),
		(u'byte6', c_uint8),
		(u'byte7', c_uint8),
		(u'byte8', c_uint8),
		(u'byte9', c_uint8),
		(u'byte10', c_uint8),
		(u'byte11', c_uint8),
		(u'byte12', c_uint8),
		(u'byte13', c_uint8),
		(u'byte14', c_uint8),
		(u'byte15', c_uint8)
	]

CFUUIDGetUUIDBytes = CoreFoundation.CFUUIDGetUUIDBytes
CFUUIDGetUUIDBytes.restype = CFUUIDBytes
CFUUIDGetUUIDBytes.argtypes = [CFUUIDRef]

CFUUIDCreateFromString = CoreFoundation.CFUUIDCreateFromString
CFUUIDCreateFromString.restype = CFUUIDRef
CFUUIDCreateFromString.argtypes = [CFAllocatorRef, CFStringRef]


# CFSet
CFSetRef = c_void_p

CFSetGetTypeID = CoreFoundation.CFSetGetTypeID
CFSetGetTypeID.restype = CFTypeID
CFSetGetTypeID.argtypes = []

CFSetGetCount = CoreFoundation.CFSetGetCount
CFSetGetCount.restype = CFIndex
CFSetGetCount.argtypes = [CFSetRef]

CFSetGetValues = CoreFoundation.CFSetGetValues
CFSetGetValues.restype = None
CFSetGetValues.argtypes = [CFSetRef, POINTER(c_void_p)]



# python/CF conversion functions
def CFTypeFrom(value):
	retval = None
	if isinstance(value, str):
		data = cast(c_char_p(value), POINTER(c_ubyte))
		retval = CFDataCreate(None, data, len(value))

	elif isinstance(value, unicode):
		retval = CFStringCreateWithCString(None, value, kCFStringEncodingUTF8)

	elif isinstance(value, bool):
		if value:
			retval = kCFBooleanTrue
		else:
			retval = kCFBooleanFalse
		CFRetain(retval)

	elif isinstance(value, int):
		v = c_long(value)
		retval = CFNumberCreate(None, kCFNumberLongType, byref(v))

	elif isinstance(value, float):
		v = c_double(value)
		retval = CFNumberCreate(None, kCFNumberDoubleType, byref(v))

	elif isinstance(value, dict):
		l = len(value.keys())
		keys = []
		values = []
		for k, v in value.iteritems():
			keys.append(CFTypeFrom(k))
			values.append(CFTypeFrom(v))

		retval = CFDictionaryCreate(
			None, 
			(c_void_p * l)(*keys), 
			(c_void_p * l)(*values), 
			l,
			byref(kCFTypeDictionaryKeyCallBacks),
			byref(kCFTypeDictionaryValueCallBacks)
		)
	elif isinstance(value, list):
		values = []
		for v in value:
			values.append(CFTypeFrom(v))
		retval = CFArrayCreate(
			None, 
			(c_void_p * len(values))(*values),
			len(value),
			byref(kCFTypeArrayCallBacks)
		)
	elif isinstance(value, datetime.datetime):
		retval = CFDateCreate(None, value.time()) # XXX sort out the origin
	else:
		raise RuntimeError(value, type(value))

	return retval


def CFTypeTo(value):
	retval = None
	typeid = CFGetTypeID(value)
	if typeid == CFStringGetTypeID():
		l = CFStringGetLength(value)
		bufsize = CFStringGetMaximumSizeForEncoding(l, kCFStringEncodingUTF8) + 1
		buf = create_string_buffer(bufsize)
		CFStringGetCString(value, buf, bufsize, kCFStringEncodingUTF8)
		retval = buf.value

	elif typeid == CFDataGetTypeID():
		retval = string_at(CFDataGetBytePtr(value), CFDataGetLength(value))

	elif typeid == CFNumberGetTypeID():
		if CFNumberIsFloatType(value):
			num = c_double()
			if CFNumberGetValue(value, kCFNumberDoubleType, byref(num)):
				retval = num.value
		else:
			num = c_long()
			if CFNumberGetValue(value, kCFNumberLongType, byref(num)):
				retval = num.value

	elif typeid == CFDictionaryGetTypeID():
		retval = {}
		l = CFDictionaryGetCount(value)
		keys = (c_void_p * l)()
		values = (c_void_p * l)()
		CFDictionaryGetKeysAndValues(value, keys, values)
		for i in range(0, l):
			key = CFTypeTo(keys[i])
			val = CFTypeTo(values[i])
			retval[key] = val

	elif typeid == CFBooleanGetTypeID():
		retval = CFBooleanGetValue(value)

	elif typeid == CFArrayGetTypeID():
		retval = []
		for i in range(0, CFArrayGetCount(value)):
			v = CFArrayGetValueAtIndex(value, i)
			retval.append(CFTypeTo(v))

	elif typeid == CFDateGetTypeID():
		retval = datetime.datetime.fromtimestamp(CFDateGetAbsoluteTime(value)) # sort out origin

	elif typeid == CFSetGetTypeID():
		retval = set()
		l = CFSetGetCount(value)
		values = (c_void_p * l)()
		CFSetGetValues(value, values)
		for i in range(0, l):
			retval.add(CFTypeTo(values[i]))
	else:
		CFShow(value)
		print(u'RuntimeError(',value, type(value), typeid)
	return retval


def dict_to_plist_encoding(d, format=kCFPropertyListBinaryFormat_v1_0):
	retval = None
	if not isinstance(d, dict):
		raise TypeError(u'd must be a dict')

	# convert the dict into a CFDictionary
	cfdict = CFTypeFrom(d)
	if cfdict is not None:
		err = CFErrorRef()
		# convert CFDictionary to CFData
		cfdata = CFPropertyListCreateData(
			None, 
			cfdict, 
			format,
			0,
			byref(err)
		)

		CFRelease(cfdict)
		if err.value != None:
			CFRelease(err)
		elif cfdata is not None:
			# convert CFData to string
			retval = CFTypeTo(cfdata)
			CFRelease(cfdata) 
	return retval


def dict_from_plist_encoding(s, format=kCFPropertyListBinaryFormat_v1_0):
	retval = None
	if not isinstance(s, str):
		raise TypeError(u's must be a str')

	# convert str to CFData
	cfdata = CFTypeFrom(s)
	if cfdata is not None:
		# convert CFData to CFDictionary
		cfdict = CFPropertyListCreateWithData(
			None,
			cfdata,
			kCFPropertyListImmutable,
			None,
			None
		)
		CFRelease(cfdata)
		if cfdict is not None:
			# convert CFDictionary to dict
			retval = CFTypeTo(cfdict)
			CFRelease(cfdict)
	return retval





