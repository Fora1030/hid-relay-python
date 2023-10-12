import threading
import ctypes
import os as _os
import sys as _sys
from ctypes.wintypes import (
    ULONG, BOOLEAN, BYTE, WORD, HANDLE, BOOL, WCHAR, LPWSTR, LPCWSTR, DWORD,
    )

hid_api_dll = ctypes.windll.hid
HidD_GetAttributes = hid_api_dll.HidD_GetAttributes

