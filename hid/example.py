from hid_api import FilterHidDevices
import time

USB_CFG_VENDOR_ID = 0x16c0  
USB_CFG_DEVICE_ID = 0x05DF  
test = FilterHidDevices(vendor_id=USB_CFG_VENDOR_ID, product_id=USB_CFG_DEVICE_ID)
device = test.get_device()
device.open()
report = None
for rep in device.find_output_reports() + device.find_feature_reports():
    report = rep
if report is not None:
    report.send([0, 0xFF, 4, 0, 0, 0, 0, 0, 1])
    time.sleep(3)
    report.send([0, 0xFD, 4, 0, 0, 0, 0, 0, 1])
device.close()