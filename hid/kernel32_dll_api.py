import ctypes
from ctypes.wintypes import BOOL, HANDLE

kernel_dll = ctypes.windll.kernel32

read_file = kernel_dll.ReadFile
cancel_io = kernel_dll.CancelIo
write_file = kernel_dll.WriteFile
close_handle = kernel_dll.CloseHandle
close_handle.restype = BOOL
close_handle.argtypes = [HANDLE]
# set_event = kernel_dll.setEvent
# wait_for_single_object = kernel_dll.WaitForSingleObject


c_tchar                         = ctypes.c_wchar
CreateFile                      = kernel_dll.CreateFileW
CreateEvent                     = kernel_dll.CreateEventW
# CM_Get_Device_ID                = setup_api.CM_Get_Device_IDW


b_verbose = True
usb_verbose = False