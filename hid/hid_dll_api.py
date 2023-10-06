import ctypes
import threading
from ctypes import Structure, Union, c_ubyte, c_long, c_ulong, c_ushort, \
        c_wchar, c_void_p, c_uint 
from ctypes.wintypes import ULONG, BOOLEAN, BYTE, WORD, DWORD, HANDLE, BOOL, \
        WCHAR, LPWSTR, LPCWSTR


hid_dll = ctypes.windll.hid

class GUID(ctypes.Structure):
    """ 
        Globally Unique Identifier Buffer
        --- 

        Pointer to a caller-allocated GUID buffer 
        that the routine uses to return the device
        interface GUID for HIDClass devices.
        retrieved from https://learn.microsoft.com/ 

    Args:
        ctypes (_type_): Structure data type frm C
    """
    _pack_ = 1
    _fields_ = [
        ("data1", DWORD), # Unsigned 4 bytes or 32 bits of data
        ("data2", WORD), # Unsigned 2 bytes or 16 bits of data 
        ("data3", WORD), 
        ("data4", BYTE * 8),
    ]

def get_hid_guid():
    hid_guid = GUID()
    hid_dll.HidD_GetHidGuid(ctypes.byref(hid_guid))
    return hid_guid

class HidDeviceBaseClass(object):
    _raw_reports_lock = threading.Lock()

    def __init__(self) -> None:
        pass

class HidDeviceCreateFile(HidDeviceBaseClass):
    def __init__(self, device_path, instance_id) -> None:
        self.device_path = device_path
        self.instance_id = instance_id
        super().__init__()
