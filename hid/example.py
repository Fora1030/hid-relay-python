from hid_api import FilterHidDevices


USB_CFG_VENDOR_ID = 0x16c0  
USB_CFG_DEVICE_ID = 0x05DF  
test = FilterHidDevices(vendor_id=USB_CFG_VENDOR_ID, product_id=USB_CFG_DEVICE_ID)
print(test.get_device())