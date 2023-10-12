from hid import FindRelay
import time

USB_CFG_VENDOR_ID = 0x16c0  
USB_CFG_DEVICE_ID = 0x05DF  
relay = FindRelay(vendor_id=USB_CFG_VENDOR_ID, product_id=USB_CFG_DEVICE_ID)
relay.open()
relay.turn_on_relay(1)
time.sleep(5)
relay.turn_off_relay(1)
relay.close()