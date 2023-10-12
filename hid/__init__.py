from hid_dll_api import GUID, get_hid_guid, HidDeviceCreateFile
from setup_dll_api import find_all_devices
from hid_api import FilterHidDevices
from kernel32_dll_api import CreateFile, CancelIo, SetEvent, WaitForSingleObject, ReadFile, WriteFile