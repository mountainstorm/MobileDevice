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

from CoreFoundation import *


# Copied from MobileDevice.h
# http://theiphonewiki.com/wiki/MobileDevice_Library#MobileDevice_Header_.28MobileDevice.h.29


if platform.system() == u'Darwin':
	MobileDevice = CDLL(u'/System/Library/PrivateFrameworks/MobileDevice.framework/MobileDevice')
elif platform.system() == u'Windows':
	raise NotImplementedError(u'need to find and import the MobileDevice dll')
else:
	raise OSError(u'Platform not supported')


# Error stuff
mach_error_t = c_int
ERR_SUCCESS = 0
ERR_MOBILE_DEVICE = 0


def err_system(x):
	return (((x) & 0x3f) << 26)

def err_sub(x):
	return (((x) & 0xfff) << 14)


# Error codes
MDERR_APPLE_MOBILE = err_system(0x3a)
MDERR_IPHONE = err_sub(0)

# Apple Mobile (AM*) errors
MDERR_OK 				= ERR_SUCCESS
MDERR_SYSCALL 			= (ERR_MOBILE_DEVICE | 0x01)
MDERR_OUT_OF_MEMORY 	= (ERR_MOBILE_DEVICE | 0x03)
MDERR_QUERY_FAILED		= (ERR_MOBILE_DEVICE | 0x04)  
MDERR_INVALID_ARGUMENT	= (ERR_MOBILE_DEVICE | 0x0b)
MDERR_DICT_NOT_LOADED	= (ERR_MOBILE_DEVICE | 0x25)


# Apple File Connection (AFC*) errors
MDERR_AFC_OUT_OF_MEMORY = 0x03

# USBMux errors
MDERR_USBMUX_ARG_NULL = 0x16
MDERR_USBMUX_FAILED = 0xffffffff

# Messages passed to device notification callbacks: passed as part of
# AMDeviceNotificationCallbackInfo
ADNCI_MSG_CONNECTED = 1
ADNCI_MSG_DISCONNECTED = 2
ADNCI_MSG_UNSUBSCRIBED = 3

AMD_IPHONE_PRODUCT_ID = 0x1290


# Services, found in /System/Library/Lockdown/Services.plist
AMSVC_BACKUP = CFSTR(u'com.apple.mobilebackup')
AMSVC_DEBUG_IMAGE_MOUNT = CFSTR(u'com.apple.mobile.debug_image_mount')
AMSVC_NOTIFICATION_PROXY = CFSTR(u'com.apple.mobile.notification_proxy')
AMSVC_PURPLE_TEST = CFSTR(u'com.apple.purpletestr')
AMSVC_SOFTWARE_UPDATE = CFSTR(u'com.apple.mobile.software_update')
AMSVC_SYNC = CFSTR(u'com.apple.mobilesync')
AMSVC_SCREENSHOT = CFSTR(u'com.apple.screenshotr')
AMSVC_SYSTEM_PROFILER = CFSTR(u'com.apple.mobile.system_profiler')

AMSVC_SPRINGBOARD_SERVICES = CFSTR(u'com.apple.springboardservices')
AMSVC_INSTALLATION_PROXY = CFSTR(u'com.apple.mobile.installation_proxy')
AMSVC_HOUSE_ARREST = CFSTR(u'com.apple.mobile.house_arrest')
AMSVC_CRASH_REPORT_COPY_MOBILE = CFSTR(u'com.apple.crashreportcopymobile')
AMSVC_AFC = CFSTR(u'com.apple.afc')
AMSVC_SYSLOG_RELAY = CFSTR(u'com.apple.syslog_relay')
AMSVC_FILE_RELAY = CFSTR(u'com.apple.mobile.file_relay')
AMSVC_WEBINSPECTOR = CFSTR(u'com.apple.webinspector')
# iosiadnositcs was the name before iOS 5, mobile.diagnostics si the new name
AMSVC_MOBILE_DIAGNOSTICS_RELAY = CFSTR("com.apple.mobile.diagnostics_relay")
AMSVC_IOSDIAGNOSTICS_RELAY = CFSTR("com.apple.iosdiagnostics.relay")


# Types
AFCError = c_uint32
USBMuxError = c_uint32


AMDeviceRef = c_void_p


AMDeviceNotificationRef = c_void_p


class AMDeviceNotificationCallbackInfo(Structure):
	_fields_ = [
		(u'device', AMDeviceRef),
		(u'message', c_uint32),
		(u'subscription', AMDeviceNotificationRef)
	]


AMDeviceNotificationCallbackInfoRef = POINTER(AMDeviceNotificationCallbackInfo)


AMDeviceNotificationCallback = CFUNCTYPE(
	None, 
	AMDeviceNotificationCallbackInfoRef,
	c_int
)


AMDDeviceAttatchedCallback = c_void_p


AMDeviceProgressCallback = CFUNCTYPE(None, CFDictionaryRef, c_int)


class AMRecoveryDevice(Structure):
	pass


AMRecoveryDeviceRef = POINTER(AMRecoveryDevice)


AMRestoreDeviceNotificationCallback = CFUNCTYPE(None, AMRecoveryDeviceRef)


AMRecoveryDevice._fields_ = [
		(u'unknown0', c_uint8),
		(u'callback', AMRestoreDeviceNotificationCallback),
		(u'userinfo', c_void_p),
		(u'unknown1', c_uint8 * 12),
		(u'readWritePipe', c_uint32),
		(u'readPipe', c_uint8),
		(u'writeControlPipe', c_uint8),
		(u'readUnknownPipe', c_uint8),
		(u'writeFilePipe', c_uint8),
		(u'writeInputPipe', c_uint8)
	]


class AMRestoreDevice(Structure):
	_fields_ = [
		(u'unknown0', c_uint8 * 8),
		(u'unknown1', c_uint8 * 24),
		(u'port', c_int32)
	]


AMRestoreDeviceRef = POINTER(AMRestoreDevice)


AMRestoreDeviceNotificationCallback = CFUNCTYPE(
	None, 
	AMRecoveryDeviceRef
)


AFCConnectionRef = c_void_p
AFCDeviceInfoRef = c_void_p
AFCDirectoryRef = c_void_p
AFCDictionaryRef = c_void_p
AFCFileRef = c_uint64


USBMuxListenerRef = c_void_p


class AMBootloaderControlPacket(Structure):
	_fields_ = [
		(u'opcode', c_uint8),
		(u'length', c_uint8),
		(u'magic', c_uint8 * 2),
	]


AMBootloaderControlPacketRef = POINTER(AMBootloaderControlPacket)


# AMDevice* routines
AMDeviceActivate = MobileDevice.AMDeviceActivate
AMDeviceActivate.restype = mach_error_t
AMDeviceActivate.argtypes = [AMDeviceRef, CFTypeRef]

# TODO: _AMDeviceArchiveApplication
# TODO: _AMDeviceCheckCapabilitiesMatch

AMDeviceConnect = MobileDevice.AMDeviceConnect
AMDeviceConnect.restype = mach_error_t
AMDeviceConnect.argtypes = [AMDeviceRef]

# AMDeviceConvertError - does nothing

# TODO: _AMDeviceCopyAuthInstallPreflightOptions

# AMDeviceCopyDeviceIdentifier - returns same value as AMDeviceGetName

AMDeviceCopyDeviceLocation = MobileDevice.AMDeviceCopyDeviceLocation
AMDeviceCopyDeviceLocation.restype = c_long
AMDeviceCopyDeviceLocation.argtypes = [AMDeviceRef]

# TODO: _AMDeviceCopyProvisioningProfiles

AMDeviceCopyValue = MobileDevice.AMDeviceCopyValue
AMDeviceCopyValue.restype = CFDictionaryRef
AMDeviceCopyValue.argtypes = [AMDeviceRef, CFStringRef, CFStringRef]

# AMDeviceCreate - not needed as we don't directly create devices
# AMDeviceCreateCopy - not needed as we don't directly create devices
# AMDeviceCreateFromProperties - not needed as we don't directly create devices
# AMDeviceCreateHouseArrestService - we only need StartHouseArrestService

# TODO: _AMDeviceCreateWakeupToken

AMDeviceDeactivate = MobileDevice.AMDeviceDeactivate
AMDeviceDeactivate.restype = mach_error_t
AMDeviceDeactivate.argtypes = [AMDeviceRef]

AMDeviceDisconnect = MobileDevice.AMDeviceDisconnect
AMDeviceDisconnect.restype = mach_error_t
AMDeviceDisconnect.argtypes = [AMDeviceRef]

AMDeviceEnterRecovery = MobileDevice.AMDeviceEnterRecovery
AMDeviceEnterRecovery.restype = mach_error_t
AMDeviceEnterRecovery.argtypes = [AMDeviceRef]

AMDeviceGetConnectionID = MobileDevice.AMDeviceGetConnectionID
AMDeviceGetConnectionID.restype = c_ulong
AMDeviceGetConnectionID.argtypes = [AMDeviceRef]

AMDeviceGetInterfaceSpeed = MobileDevice.AMDeviceGetInterfaceSpeed
AMDeviceGetInterfaceSpeed.restype = c_ulong
AMDeviceGetInterfaceSpeed.argtypes = [AMDeviceRef]

AMDeviceGetInterfaceType = MobileDevice.AMDeviceGetInterfaceType
AMDeviceGetInterfaceType.restype = c_long
AMDeviceGetInterfaceType.argtypes = [AMDeviceRef]

# AMDeviceGetLocalOrRemoteOffsetToResume - dont think we need

AMDeviceGetName = MobileDevice.AMDeviceGetName
AMDeviceGetName.restype = CFStringRef
AMDeviceGetName.argtypes = [AMDeviceRef]

# AMDeviceGetTypeID - dont need; returns the CFTypeID for AMDeviceRef

# TODO: AMDeviceGetUserInfo - no idea; returns AMDeviceRef + 96

AMDeviceGetWirelessBuddyFlags = MobileDevice.AMDeviceGetWirelessBuddyFlags
AMDeviceGetWirelessBuddyFlags.restype = mach_error_t
AMDeviceGetWirelessBuddyFlags.argtypes = [AMDeviceRef, POINTER(CFTypeRef)]

AMDeviceInstallApplication = MobileDevice.AMDeviceInstallApplication
AMDeviceInstallApplication.restype = mach_error_t
AMDeviceInstallApplication.argtypes = [
	c_uint32, 
	CFStringRef, 
	CFDictionaryRef, 
	AMDeviceProgressCallback, 
	c_void_p
]

# AMDeviceInstallPackage - appears to be legacy install (uses Nikita)

# TODO: AMDeviceInstallProvisioningProfile

AMDeviceIsPaired = MobileDevice.AMDeviceIsPaired
AMDeviceIsPaired.restype = mach_error_t
AMDeviceIsPaired.argtypes = [AMDeviceRef]

# AMDeviceIsValid - I think it checks if we're connected

# AMDeviceLookupApplicationArchives - legacy version of AMDeviceLookupApplications
# AMDeviceLookupApplications - sends Browse to installation_proxy; we do directly

AMDeviceMountImage = MobileDevice.AMDeviceMountImage
AMDeviceMountImage.restype = mach_error_t
AMDeviceMountImage.argtypes = [
	AMDeviceRef, 
	CFStringRef, 
	CFDictionaryRef, 
	AMDeviceProgressCallback, 
	c_void_p
]

AMDeviceNotificationSubscribe = MobileDevice.AMDeviceNotificationSubscribe
AMDeviceNotificationSubscribe.restype = mach_error_t
AMDeviceNotificationSubscribe.argtypes = [
	AMDeviceNotificationCallback, 
	c_uint32, 
	c_uint32, 
	c_uint32,
	POINTER(AMDeviceNotificationRef)
]

AMDeviceNotificationUnsubscribe = MobileDevice.AMDeviceNotificationUnsubscribe
AMDeviceNotificationUnsubscribe.restype = mach_error_t
AMDeviceNotificationUnsubscribe.argtypes = [AMDeviceNotificationRef]

# AMDevicePair - not needed
# AMDevicePairWithOptions - not needed
# AMDevicePreflightOperationCreate - no idea
# AMDevicePreflightOperationGetRunLoopSource - no idea
# AMDevicePreflightOperationGetTypeID - no idea
# AMDevicePreflightOperationInvalidate - no idea

AMDeviceRelease = MobileDevice.AMDeviceRelease
AMDeviceRelease.restype = None
AMDeviceRelease.argtypes = [AMDeviceRef]

# AMDeviceRemoveApplicationArchive - I'm guessing its the legacy version of AMDeviceSecureUninstallApplication

# TODO: AMDeviceRemoveProvisioningProfile

AMDeviceRemoveValue = MobileDevice.AMDeviceRemoveValue
AMDeviceRemoveValue.restype = mach_error_t
AMDeviceRemoveValue.argtypes = [AMDeviceRef, CFStringRef, CFStringRef]

# TODO: AMDeviceSecureRestoreApplication

# AMDeviceRetain - we don't need currently
# AMDeviceSecureArchiveApplication - we will use the non-secure wrapper
# AMDeviceSecureCheckCapabilitiesMatch - we will use the non-secure wrapper
# AMDeviceSecureInstallApplication - we will use the non-secure wrapper
# AMDeviceSecureRemoveApplicationArchive - legacy, not needed
# AMDeviceSecureRestoreApplication - we will use the non-secure wrapper
# AMDeviceSecureStartService - we will use the non-secure wrapper
# AMDeviceSecureTransferPath - we will use the non-secure wrapper
# AMDeviceSecureUninstallApplication - we will use the non-secure wrapper
# AMDeviceSecureUpgradeApplication - we will use the non-secure wrapper
# AMDeviceSetUserInfo - not needed; sets the user info member of AMDeviceRef
 
AMDeviceSetValue = MobileDevice.AMDeviceSetValue
AMDeviceSetValue.restype = mach_error_t
AMDeviceSetValue.argtypes = [AMDeviceRef, CFStringRef, CFStringRef, CFTypeRef]

AMDeviceSetWirelessBuddyFlags = MobileDevice.AMDeviceSetWirelessBuddyFlags
AMDeviceSetWirelessBuddyFlags.restype = mach_error_t
AMDeviceSetWirelessBuddyFlags.argtypes = [AMDeviceRef, c_long]

# AMDeviceStartHouseArrestService - we're doing it manually

# AMDeviceStartService - we always use the withOptions variant

AMDeviceStartServiceWithOptions = MobileDevice.AMDeviceStartServiceWithOptions
AMDeviceStartServiceWithOptions.restype = mach_error_t
AMDeviceStartServiceWithOptions.argtypes = [
	AMDeviceRef, 
	CFStringRef, 
	CFDictionaryRef,
	POINTER(c_int32)
]

AMDeviceStartSession = MobileDevice.AMDeviceStartSession
AMDeviceStartSession.restype = mach_error_t
AMDeviceStartSession.argtypes = [AMDeviceRef]

AMDeviceStopSession = MobileDevice.AMDeviceStopSession
AMDeviceStopSession.restype = mach_error_t
AMDeviceStopSession.argtypes = [AMDeviceRef]

AMDeviceTransferApplication = MobileDevice.AMDeviceTransferApplication
AMDeviceTransferApplication.restype = mach_error_t
AMDeviceTransferApplication.argtypes = [
	c_int32, 
	CFStringRef, 
	c_void_p, 
	AMDeviceProgressCallback, 
	c_void_p
]

# TODO: AMDeviceTransferPath

AMDeviceUSBDeviceID = MobileDevice.AMDeviceUSBDeviceID
AMDeviceUSBDeviceID.restype = c_long
AMDeviceUSBDeviceID.argtypes = [AMDeviceRef]

# AMDeviceUSBLocationID - we get the same info by using AMDeviceCopyDeviceLocation

AMDeviceUSBProductID = MobileDevice.AMDeviceUSBProductID
AMDeviceUSBProductID.restype = c_long
AMDeviceUSBProductID.argtypes = [AMDeviceRef]

# TODO: AMDeviceUninstallApplication
# TODO: AMDeviceUninstallPackage

AMDeviceUnpair = MobileDevice.AMDeviceUnpair
AMDeviceUnpair.restype = mach_error_t
AMDeviceUnpair.argtypes = [AMDeviceRef]

AMDeviceUpgradeApplication = MobileDevice.AMDeviceUpgradeApplication
AMDeviceUpgradeApplication.restype = mach_error_t
AMDeviceUpgradeApplication.argtypes = [
	c_uint32, 
	CFStringRef, 
	CFDictionaryRef, 
	AMDeviceProgressCallback, 
	c_void_p
]

AMDeviceValidatePairing = MobileDevice.AMDeviceValidatePairing
AMDeviceValidatePairing.restype = mach_error_t
AMDeviceValidatePairing.argtypes = [AMDeviceRef]

# TODO: AMDeviceWakeupOperationCreateWithToken ??

# AMDeviceWakeupOperationGetTypeID - CFTypeID for WakeOperation

# TODO: AMDeviceWakeupOperationInvalidate
# TODO: AMDeviceWakeupOperationSchedule
# TODO: AMDeviceWakeupUsingToken

AMDeviceConnectByAddressAndPort = MobileDevice._AMDeviceConnectByAddressAndPort
AMDeviceConnectByAddressAndPort.restype = mach_error_t
AMDeviceConnectByAddressAndPort.argtypes = [
	AMDeviceRef, 
	c_ushort, 
	POINTER(c_int32)
]


#AMD* methods
AMDSetLogLevel = MobileDevice.AMDSetLogLevel
AMDSetLogLevel.restype = c_int
AMDSetLogLevel.argtypes = [c_int]


# USBMux* methods
USBMuxConnectByPort = MobileDevice.USBMuxConnectByPort
USBMuxConnectByPort.restype = mach_error_t
USBMuxConnectByPort.argtypes = [
	c_uint32, 
	c_ushort, 
	POINTER(c_int32)
]

USBMuxListenerSetDebug = MobileDevice.USBMuxListenerSetDebug
USBMuxListenerSetDebug.restype = c_int32
USBMuxListenerSetDebug.argtypes = [c_int32]





AFCConnectionOpen = MobileDevice.AFCConnectionOpen
AFCConnectionOpen.restype = AFCError
AFCConnectionOpen.argtypes = [c_int32, c_uint32, POINTER(AFCConnectionRef)]

# TODO: not found
#AMRecoveryModeCopyEnvironmentVariable = MobileDevice.AMRecoveryModeCopyEnvironmentVariable
#AMRecoveryModeCopyEnvironmentVariable.restype = CFStringRef
#AMRecoveryModeCopyEnvironmentVariable.argtypes = [
#	AMRecoveryDeviceRef, 
#	CFStringRef
#]

AFCDeviceInfoOpen = MobileDevice.AFCDeviceInfoOpen
AFCDeviceInfoOpen.restype = AFCError
AFCDeviceInfoOpen.argtypes = [AFCConnectionRef, POINTER(AFCDictionaryRef)]

if platform.system() == u'Darwin':
	AFCPlatformInitialize = MobileDevice.AFCPlatformInitialize
	AFCPlatformInitialize.restype = None
	AFCPlatformInitialize.argtypes = []

AFCDirectoryOpen = MobileDevice.AFCDirectoryOpen
AFCDirectoryOpen.restype = AFCError
AFCDirectoryOpen.argtypes = [
	AFCConnectionRef, 
	c_char_p, 
	POINTER(AFCDirectoryRef)
]

AFCDirectoryRead = MobileDevice.AFCDirectoryRead
AFCDirectoryRead.restype = AFCError
AFCDirectoryRead.argtypes = [AFCConnectionRef, AFCDirectoryRef, POINTER(c_char_p)]

AFCDirectoryClose = MobileDevice.AFCDirectoryClose
AFCDirectoryClose.restype = AFCError
AFCDirectoryClose.argtypes = [AFCConnectionRef, AFCDirectoryRef]

AFCDirectoryCreate = MobileDevice.AFCDirectoryCreate
AFCDirectoryCreate.restype = AFCError
AFCDirectoryCreate.argtypes = [AFCConnectionRef, c_char_p]

AFCRemovePath = MobileDevice.AFCRemovePath
AFCRemovePath.restype = AFCError
AFCRemovePath.argtypes = [AFCConnectionRef, c_char_p]

AFCRenamePath = MobileDevice.AFCRenamePath
AFCRenamePath.restype = AFCError
AFCRenamePath.argtypes = [AFCConnectionRef, c_char_p, c_char_p]


# TODO: if ITUNES_VER >= 800
if 1:
	AFCLinkPath = MobileDevice.AFCLinkPath
	AFCLinkPath.restype = AFCError
	AFCLinkPath.argtypes = [AFCConnectionRef, c_int64, c_char_p, c_char_p]


AFCFileRefOpen = MobileDevice.AFCFileRefOpen
AFCFileRefOpen.restype = AFCError
AFCFileRefOpen.argtypes = [
	AFCConnectionRef,
	c_char_p,
	c_uint64,
	POINTER(AFCFileRef)
]

AFCFileRefRead = MobileDevice.AFCFileRefRead
AFCFileRefRead.restype = AFCError
AFCFileRefRead.argtypes = [
	AFCConnectionRef, 
	AFCFileRef, 
	c_void_p, 
	POINTER(c_uint32)
]

AFCFileRefWrite = MobileDevice.AFCFileRefWrite
AFCFileRefWrite.restype = AFCError
AFCFileRefWrite.argtypes = [
	AFCConnectionRef,
	AFCFileRef,
	c_void_p,
	c_uint32
]

AFCFileRefSeek = MobileDevice.AFCFileRefSeek
AFCFileRefSeek.restype = AFCError
AFCFileRefSeek.argtypes = [
	AFCConnectionRef,
	AFCFileRef,
	CFIndex,
	c_int32,
	c_int32
]

AFCFileRefTell = MobileDevice.AFCFileRefTell
AFCFileRefTell.restype = AFCError
AFCFileRefTell.argtypes = [AFCConnectionRef, AFCFileRef, POINTER(CFIndex)]

AFCFileRefSetFileSize = MobileDevice.AFCFileRefSetFileSize
AFCFileRefSetFileSize.restype = AFCError
AFCFileRefSetFileSize.argtypes = [AFCConnectionRef, AFCFileRef, CFIndex]

AFCFileRefLock = MobileDevice.AFCFileRefLock
AFCFileRefLock.restype = AFCError
AFCFileRefLock.argtypes = [AFCConnectionRef, AFCFileRef]

AFCFileRefUnlock = MobileDevice.AFCFileRefUnlock
AFCFileRefUnlock.restype = AFCError
AFCFileRefUnlock.argtypes = [AFCConnectionRef, AFCFileRef]

AFCFileRefClose = MobileDevice.AFCFileRefClose
AFCFileRefClose.restype = AFCError
AFCFileRefClose.argtypes = [AFCConnectionRef, AFCFileRef]

AFCFileInfoOpen = MobileDevice.AFCFileInfoOpen
AFCFileInfoOpen.restype = AFCError
AFCFileInfoOpen.argtypes = [
	AFCConnectionRef, 
	c_char_p, 
	POINTER(AFCDictionaryRef)
]

AFCKeyValueRead = MobileDevice.AFCKeyValueRead
AFCKeyValueRead.restype = AFCError
AFCKeyValueRead.argtypes = [
	AFCDictionaryRef, 
	POINTER(c_char_p), 
	POINTER(c_char_p)
]

AFCKeyValueClose = MobileDevice.AFCKeyValueClose
AFCKeyValueClose.restype = AFCError
AFCKeyValueClose.argtypes = [AFCDictionaryRef]

AFCConnectionGetContext = MobileDevice.AFCConnectionGetContext
AFCConnectionGetContext.restype = c_uint32
AFCConnectionGetContext.argtypes = [AFCConnectionRef]

AFCConnectionGetFSBlockSize = MobileDevice.AFCConnectionGetFSBlockSize
AFCConnectionGetFSBlockSize.restype = c_uint32
AFCConnectionGetFSBlockSize.argtypes = [AFCConnectionRef]

AFCConnectionGetIOTimeout = MobileDevice.AFCConnectionGetIOTimeout
AFCConnectionGetIOTimeout.restype = c_uint32
AFCConnectionGetIOTimeout.argtypes = [AFCConnectionRef]

AFCConnectionGetSocketBlockSize = MobileDevice.AFCConnectionGetSocketBlockSize
AFCConnectionGetSocketBlockSize.restype = c_uint32
AFCConnectionGetSocketBlockSize.argtypes = [AFCConnectionRef]

AFCConnectionClose = MobileDevice.AFCConnectionClose
AFCConnectionClose.restype = AFCError
AFCConnectionClose.argtypes = [AFCConnectionRef]

AMRestoreRegisterForDeviceNotifications = MobileDevice.AMRestoreRegisterForDeviceNotifications
AMRestoreRegisterForDeviceNotifications.restype = c_uint32
AMRestoreRegisterForDeviceNotifications.argtypes = [
	AMRestoreDeviceNotificationCallback,
	AMRestoreDeviceNotificationCallback,
	AMRestoreDeviceNotificationCallback,
	AMRestoreDeviceNotificationCallback,
	c_uint32,
	c_void_p
]

AMRestoreEnableFileLogging = MobileDevice.AMRestoreEnableFileLogging
AMRestoreEnableFileLogging.restype = c_uint32
AMRestoreEnableFileLogging.argtypes = [c_char_p]

#AMRestoreCreateDefaultOptions = MobileDevice.AMRestoreCreateDefaultOptions
#AMRestoreCreateDefaultOptions.restype = CFMutableDictionaryRef
#AMRestoreCreateDefaultOptions.argtypes = [CFAllocatorRef]

# extras not in MobileDevice.h





