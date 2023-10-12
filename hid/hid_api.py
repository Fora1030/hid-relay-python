from setup_dll_api import find_all_devices
from hid_dll_api import HidDeviceCreateFile

class FilterHidDevices(object):
    """ 
    Filtering HID devices
    ---

        This class searches for all hid devices and filters 
        the targeted device.
        


    Args:
        object (_type_): _description_
    """
    def __init__(self, vendor_id, product_id) -> None:
        """
        Constructor to search and filter all hid devices.
        ---

        Args:
            vendor_id (hexadecimal): hexadecimal id
            product_id (hexadecimal): hexadecimal id 
        """
        self.vendor_id = vendor_id
        self.product_id = product_id
    
    def find_device_path(self):
        all_devices = find_all_devices()
        print(all_devices)
        for device_path in  all_devices:
            if (str(hex(self.vendor_id))[2:] in device_path and str(hex(self.product_id))[2:] in device_path):
                return device_path
        raise Exception("The device was not found!")

    def get_device(self):
        device_path = self.find_device_path()
        hid_device = HidDeviceCreateFile(device_path= device_path, instance_id="")
        print(hid_device.open())
