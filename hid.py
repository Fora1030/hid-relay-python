import ctypes
from ctypes.wintypes import (
    ULONG, BOOLEAN, BYTE, WORD, HANDLE, BOOL, WCHAR, LPWSTR, LPCWSTR, DWORD,
    TCHAR
    )
import platform 

if platform.architecture()[0].startswith('64'):
    WIN_PACK = 8
else:
    WIN_PACK = 1

hid_dll = ctypes.windll.hid
setup_api_dll = ctypes.windll.setupapi
kernel32_dll = ctypes.windll.kernel32

class GUID(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("data1", DWORD),
        ("data2", WORD),
        ("data3", WORD),
        ("data4", BYTE * 8), # 64 bits
    ]

class DIGCF:
    DEFAULT         = 0x00000001 
    PRESENT         = 0x00000002
    ALLCLASSES      = 0x00000004
    PROFILE         = 0x00000008
    DEVICEINTERFACE = 0x00000010

class SP_DEVICE_INTERFACE_DATA(ctypes.Structure): #FIXME: needed #NOTE: learn structure type
    _pack_ = WIN_PACK
    _fields_ = [ \
            ("cb_size",              DWORD),
            ("interface_class_guid", GUID),
            ("flags",                DWORD),
            ("reserved",             ctypes.POINTER(ULONG))
    ]
class SP_DEVINFO_DATA(ctypes.Structure):
    _pack_ = WIN_PACK
    _fields_ = [
        ("cb_size", DWORD),
        ("class_guid", GUID),
        ("dev_inst", DWORD),
        ("reserved", ctypes.POINTER(ULONG)),
    ]
class SP_DEVICE_INTERFACE_DETAIL_DATA(Structure):#NOTE Needed
    """
    typedef struct _SP_DEVICE_INTERFACE_DETAIL_DATA {
      DWORD cbSize;
      TCHAR DevicePath[ANYSIZE_ARRAY];
    } SP_DEVICE_INTERFACE_DETAIL_DATA, *PSP_DEVICE_INTERFACE_DETAIL_DATA;
    """
    _pack_ = WIN_PACK
    _fields_ = [ \
            ("cb_size",     DWORD),
            ("device_path", WCHAR * 1) # device_path[1]
    ]
    def get_string(self):#NOTE: needed
        """Retreive stored string"""
        return ctypes.wstring_at(ctypes.byref(self, ctypes.sizeof(DWORD)))


class DeviceInterfaceSetInfo():
    def __init__(self, guid_target) -> None:
        self.guid = guid_target
        self.h_info = None
    
    def __enter__(self):
        return self.open()
    
    def open(self):
        self.h_info = SetupDiGetClassDevs(ctypes.byref(self.guid), None, None,
            (DIGCF.PRESENT | DIGCF.DEVICEINTERFACE)
        )
        return self.h_info
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def close(self):
        if self.h_info and self.h_info != HANDLE(-1):
            SetupDiDestroyDeviceInfoList(self.h_info)
        self.h_info = None

SetupDiGetDeviceInterfaceDetail = setup_api_dll.SetupDiGetDeviceInterfaceDetailW
SetupDiGetDeviceInterfaceDetail.restype = BOOL
SetupDiGetDeviceInterfaceDetail.argtypes = [
    HANDLE, # __in       HDEVINFO DeviceInfoSet,
    ctypes.POINTER(SP_DEVICE_INTERFACE_DATA), # __in PSP_DEVICE_INTERFACE_DATA DeviceIn
    # __out_opt  PSP_DEVICE_INTERFACE_DETAIL_DATA DeviceInterfaceDetailData,
    ctypes.POINTER(SP_DEVICE_INTERFACE_DETAIL_DATA),
    DWORD, # __in       DWORD DeviceInterfaceDetailDataSize,
    ctypes.POINTER(DWORD), # __out_opt  PDWORD RequiredSize,
    ctypes.POINTER(SP_DEVINFO_DATA), # __out_opt  PSP_DEVINFO_DATA DeviceInfoData
    ]
SetupDiGetClassDevs = setup_api_dll.SetupDiGetClassDevsw
SetupDiGetClassDevs.restype  = HANDLE
SetupDiGetClassDevs.argtypes = [
    ctypes.POINTER(GUID), # __in_opt  const GUID *ClassGuid,
    LPCWSTR, # __in_opt  PCTSTR Enumerator,
    HANDLE,  # __in_opt  HWND hwndParent,
    DWORD,   # __in      DWORD Flags
    ]
SetupDiDestroyDeviceInfoList = setup_api_dll.SetupDiDestroyDeviceInfoList
SetupDiDestroyDeviceInfoList.restype = BOOL
SetupDiDestroyDeviceInfoList.argtypes = [
    HANDLE, # __in       HDEVINFO DeviceInfoSet,
    ]


SetupDiEnumDeviceInterfaces = setup_api_dll.SetupDiEnumDeviceInterfaces
SetupDiEnumDeviceInterfaces.restype = BOOL
SetupDiEnumDeviceInterfaces.argtypes = [
    HANDLE,                     # _In_ HDEVINFO DeviceInfoSet,
    ctypes.POINTER(SP_DEVINFO_DATA),   # _In_opt_ PSP_DEVINFO_DATA DeviceInfoData,
    ctypes.POINTER(GUID),              # _In_ const GUIDi *InterfaceClassGuid,
    DWORD,                      # _In_ DWORD MemberIndex,
    ctypes.POINTER(SP_DEVICE_INTERFACE_DATA), # _Out_ PSP_DEVICE_INTERFACE_DATA DeviceInterfaceData
    ]

def hid_filter(**kwargs):
    return kwargs

def enum_device_interfaces(h_info, guid):
    dev_interface_data = SP_DEVICE_INTERFACE_DATA()
    dev_interface_data.cd_size = ctypes.sizeof(dev_interface_data)
    device_index = 0

    while SetupDiEnumDeviceInterfaces(h_info,
            None,
            ctypes.byref(guid),
            device_index,
            ctypes.byref(dev_interface_data) ):

        yield dev_interface_data
        device_index += 1
    del dev_interface_data

def get_device_path(h_info, interface_data, ptr_info_data=None):
    required_size = ctypes.c_ulong(0)
    dev_inter_detail_data = SP_DEVICE_INTERFACE_DETAIL_DATA()
    dev_inter_detail_data.cb_size = ctypes.sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA)

    SetupDiGetDeviceInterfaceDetail(
        h_info, ctypes.byref(interface_data), None, 0, ctypes.byref(required_size), None
        )
    ctypes.resize(dev_inter_detail_data, required_size.value)

    SetupDiGetDeviceInterfaceDetail(
        h_info, ctypes.byref(interface_data), ctypes.byref(dev_inter_detail_data), 
        required_size, None, ptr_info_data
        )
    return dev_inter_detail_data.get_string()


def get_devices():
    guid = get_hid_guid()

    result = []
    require_size = DWORD

    info_data =  SP_DEVINFO_DATA()
    info_data.cb_size = ctypes.sizeof(SP_DEVINFO_DATA)

    with DeviceInterfaceSetInfo(guid) as h_info:
        for interface_data in enum_device_interfaces(h_info, guid):
            device_path = get_device_path(h_info, interface_data, ctypes.byref(info_data))
            parent_device = ctypes.c_ulong()

            

            ...
            


def get_hid_guid():
    hid_guid = GUID()
    hid_dll.hidD_GetHidGuid(ctypes.byref(hid_guid))
    return hid_guid




print(f"{get_devices()}")