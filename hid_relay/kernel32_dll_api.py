import ctypes
from ctypes.wintypes import BOOL, HANDLE

kernel_dll = ctypes.windll.kernel32

ReadFile = kernel_dll.ReadFile
CancelIo = kernel_dll.CancelIo
WriteFile = kernel_dll.WriteFile
close_handle = kernel_dll.CloseHandle
close_handle.restype = BOOL
close_handle.argtypes = [HANDLE]
SetEvent            = kernel_dll.SetEvent
WaitForSingleObject = kernel_dll.WaitForSingleObject



c_tchar                         = ctypes.c_wchar
CreateFile                      = kernel_dll.CreateFileW
CreateEvent                     = kernel_dll.CreateEventW
# CM_Get_Device_ID                = setup_api.CM_Get_Device_IDW


b_verbose = True
usb_verbose = False