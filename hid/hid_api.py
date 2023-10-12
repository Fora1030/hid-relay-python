from setup_dll_api import find_all_devices
from hid_dll_api import HidDeviceCreateFile

class FindRelay(object): 
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
        self.relay = None
        self.report = None
    
    def find_device_path(self):
        all_devices = find_all_devices()
        # print(all_devices)
        for device_path in  all_devices:
            if (str(hex(self.vendor_id))[2:] in device_path and str(hex(self.product_id))[2:] in device_path):
                return device_path
        raise Exception("The device was not found!")

    def get_device(self):
        device_path = self.find_device_path()
        hid_device = HidDeviceCreateFile(device_path= device_path, instance_id="")
        return hid_device

    def open(self):
        self.relay = self.get_device()
        if not self.relay.is_opened():
            self.relay.open()
            for rep in self.relay.find_output_reports() + self.relay.find_feature_reports():
                self.report = rep
            return True
        else:
            raise Exception("The relay is already in use!")
    
    def close(self):
        if self.relay.is_opened():
            self.relay.close()
        else:
            raise Exception("Relay is not opened!")
    
    def turn_on_relay(self, relay_number=1):
        """
            Turns target relay on.

        Args:
            relay_number (int, optional): _description_. Defaults to 1.
        """
        if self.report is not None:
            self.report.send([0, 0xFF, relay_number, 0, 0, 0, 0, 0, 1])
            return True
        else:
            return False

    def turn_off_relay(self, relay_number=1):
        """
            Turns target relay off.
            

        Args:
            relay_number (int, optional): _description_. Defaults to 1.
        """
        if self.report is not None:
            self.report.send([0, 0xFD, relay_number, 0, 0, 0, 0, 0, 1])
            return True
        else:
            return False