import ctypes
from ctypes import Structure, Union, c_ubyte, c_long, c_ulong, c_ushort, \
        c_wchar, c_void_p, c_uint 
from ctypes.wintypes import ULONG, BOOLEAN, BYTE, WORD, DWORD, HANDLE, BOOL, \
        WCHAR, LPWSTR, LPCWSTR

from hid_dll_api import GUID

setup_dll = ctypes.windll.setupapi


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


class SP_DEVINFO_DATA(ctypes.Structure):
    """
        C structure that specifies a device information element
    """
    _pack_ = 8 # for 64 bits
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
    _pack_ = 8
    _fields_ = [ \
            ("cb_size",              DWORD),
            ("interface_class_guid", GUID),
            ("flags",                DWORD),
            ("reserved",             ctypes.POINTER(ULONG))
    ]

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
    
    def __exit__(self):
        self.close()

    def close(self):
        """Destroy allocated storage"""
        if self.handle_info and self.handle_info != (HANDLE(-1)):
            SetupDiDestroyDeviceInfoList(self.handle_info)
        self.handle_info = None

def enum_device_interfaces(handle_info, guid):
    dev_interface_data = SP_DEVICE_INTERFACE_DATA()
    dev_interface_data.cb_size = ctypes.sizeof(SP_DEVICE_INTERFACE_DATA)

    device_index = 0
    while SetupDiEnumDeviceInterfaces(
            handle_info, None, ctypes.byref(guid), 
            device_index, ctypes.byref(dev_interface_data)
        ):
        yield dev_interface_data
        device_index += 1
    del dev_interface_data


    ...

def find_all_divices():
    guid = GUID()
    results = []
    required_size = DWORD()

    info_data = SP_DEVINFO_DATA()
    info_data.cb_size = ctypes.sizeof(SP_DEVINFO_DATA)
    with DeviceInformationSetInterface(guid) as handle_info:
        for interface_data in enum_device_interfaces(handle_info, guid):
            ...
    handle = SetupDiGetClassDevsW(ctypes.byref(guid), None, None, (DIGCF.PRESENT | DIGCF.DEVICEINTERFACE))
    print(handle)
    print(SetupDiDestroyDeviceInfoList(handle))