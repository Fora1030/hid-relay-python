import sys as _sys
import ctypes
from ctypes import Structure, Union, c_ubyte, c_long, c_ulong, c_ushort, \
        c_wchar, c_void_p, c_uint 
from ctypes.wintypes import ULONG, BOOLEAN, BYTE, WORD, DWORD, HANDLE, BOOL, \
        WCHAR, LPWSTR, LPCWSTR
from hid_dll_api import GUID, get_hid_guid
import platform

setup_dll = ctypes.windll.setupapi

if platform.architecture()[0].startswith('64'):
    WIN_PACK = 8
else:
    WIN_PACK = 1

class DIGCF:
    """
    Flags controlling what is included in the device information set built
    by SetupDiGetClassDevs
    """
    DEFAULT         = 0x00000001  
    PRESENT         = 0x00000002
    ALLCLASSES      = 0x00000004
    PROFILE         = 0x00000008
    DEVICEINTERFACE = 0x00000010


class SP_DEVINFO_DATA(Structure):
    """
        C structure that specifies a device information element
    """
    _pack_ = WIN_PACK 
    _fields_ = [
        ("cb_size", DWORD),
        ("class_guid", GUID),
        ("dev_inst", DWORD),
        ("reserved", ctypes.POINTER(ULONG)),
    ]

class SP_DEVICE_INTERFACE_DATA(Structure):
    """
        An SP_DEVICE_INTERFACE_DATA structure defines a device 
        interface in a device information set.
    """
    _pack_ = WIN_PACK
    _fields_ = [ \
            ("cb_size",              DWORD),
            ("interface_class_guid", GUID),
            ("flags",                DWORD),
            ("reserved",             ctypes.POINTER(ULONG))
    ]

class SP_DEVICE_INTERFACE_DETAIL_DATA(Structure):
    """ Structure to receive information about the the specified interface"""
    _pack_ = WIN_PACK
    _fields_ = [
        ("cb_size", DWORD),
        ("device_path", WCHAR*1),
    ]

    def __str__(self) -> str:
        return ctypes.wstring_at(ctypes.byref(self, ctypes.sizeof(DWORD)))

SetupDiGetClassDevsW = setup_dll.SetupDiGetClassDevsW
SetupDiGetClassDevsW.restype = HANDLE
SetupDiGetClassDevsW.argtypes = [
    ctypes.POINTER(GUID),
    LPCWSTR,
    HANDLE,
    DWORD,
]

SetupDiEnumDeviceInterfaces = setup_dll.SetupDiEnumDeviceInterfaces
SetupDiEnumDeviceInterfaces.restype = BOOL
SetupDiEnumDeviceInterfaces.argtypes = [
    HANDLE,                     
    ctypes.POINTER(SP_DEVINFO_DATA),
    ctypes.POINTER(GUID),
    DWORD,
    ctypes.POINTER(SP_DEVICE_INTERFACE_DATA),
    ]


SetupDiDestroyDeviceInfoList = setup_dll.SetupDiDestroyDeviceInfoList
SetupDiDestroyDeviceInfoList.restype = BOOL
SetupDiDestroyDeviceInfoList.argtypes = [HANDLE]

SetupDiGetDeviceInterfaceDetail = setup_dll.SetupDiGetDeviceInterfaceDetailW
SetupDiGetDeviceInterfaceDetail.restype = BOOL
SetupDiGetDeviceInterfaceDetail.argtypes = [
    HANDLE,
    ctypes.POINTER(SP_DEVICE_INTERFACE_DATA),
    ctypes.POINTER(SP_DEVICE_INTERFACE_DETAIL_DATA),
    DWORD,
    ctypes.POINTER(DWORD),
    ctypes.POINTER(SP_DEVINFO_DATA),
    ]

SetupDiGetDeviceInstanceId          = setup_dll.SetupDiGetDeviceInstanceIdW #NOTE needed
SetupDiGetDeviceInstanceId.restype  = BOOL
SetupDiGetDeviceInstanceId.argtypes = [
    HANDLE,
    ctypes.POINTER(SP_DEVINFO_DATA), 
    LPWSTR,
    DWORD,
    ctypes.POINTER(DWORD), 
    ]


class DeviceInformationSetInterface(object):
    """
        Interface for SetupDiGetClassDevsW function (setupapi.h) which returns a handle 
        to a device information set that contains requested device information elements for
        a local computer.    

    Args:
        object (_type_): _description_
    """
    def __init__(self, guid_target) -> None:
        self.guid = guid_target
        self.handle_info = None

    def __enter__(self):
        return self.open()
    
    def open(self):
        """
            Gets handle to an opaque device information set that describes the device interfaces

        """
        self.handle_info = SetupDiGetClassDevsW(
            ctypes.byref(self.guid), None, None, (DIGCF.PRESENT | DIGCF.DEVICEINTERFACE)
        )
        return self.handle_info
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """Destroy allocated storage"""
        if self.handle_info and self.handle_info != (HANDLE(-1)):
            SetupDiDestroyDeviceInfoList(self.handle_info)
        self.handle_info = None

def create_unicode_buffer(init, size=None):
    if isinstance(init, str):
        if size is None:
            if ctypes.sizeof(c_wchar) == 2:
                size = sum(2 if ord(c) > 0xFFFF else 1 for c in init) + 1
            else:
                size = len(init) + 1
        _sys.audit("ctypes.create_unicode_buffer", init, size)
        buftype = c_wchar * size
        buf = buftype()
        buf.value = init
        return buf
    elif isinstance(init, int):
        _sys.audit("ctypes.create_unicode_buffer", None, init)
        buftype = c_wchar * init
        buf = buftype()
        return buf
    raise TypeError(init)

def enum_device_interfaces(handle_info, guid):
    dev_interface_data = SP_DEVICE_INTERFACE_DATA()
    dev_interface_data.cb_size = ctypes.sizeof(dev_interface_data)

    device_index = 0
    while SetupDiEnumDeviceInterfaces(
            handle_info, None, ctypes.byref(guid), 
            device_index, ctypes.byref(dev_interface_data)
        ):
        yield dev_interface_data
        device_index += 1
    del dev_interface_data

def get_device_path(handle_info, interface_data, ptr_info_data= None):
    required_size = c_ulong(0)
    dev_interface_detail_data = SP_DEVICE_INTERFACE_DETAIL_DATA()
    dev_interface_detail_data.cb_size = ctypes.sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA)

    # get storage requirement 
    SetupDiGetDeviceInterfaceDetail(
        handle_info, ctypes.byref(interface_data), 
        None, 0, ctypes.byref(required_size), None)
    
    ctypes.resize(dev_interface_detail_data, required_size.value)

    SetupDiGetDeviceInterfaceDetail(
        handle_info, ctypes.byref(interface_data),
        ctypes.byref(dev_interface_detail_data), # get value
        required_size, None, ptr_info_data
        )
    return dev_interface_detail_data.__str__()

def find_all_devices():
    guid = get_hid_guid()
    results = []
    required_size = DWORD()

    info_data = SP_DEVINFO_DATA()
    info_data.cb_size = ctypes.sizeof(SP_DEVINFO_DATA)
    with DeviceInformationSetInterface(guid) as handle_info:
        for interface_data in enum_device_interfaces(handle_info, guid):
            device_path = get_device_path(handle_info, interface_data, ctypes.byref(info_data))
            # print("path", device_path)
            results.append(device_path)
    return results

