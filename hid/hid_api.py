
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
    
    def find_device(self):
        pass

    def filter_device(self):
        ...