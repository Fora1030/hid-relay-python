import ctypes
import threading
from ctypes import Structure, Union, c_ubyte, c_long, c_ulong, c_ushort, \
        c_wchar, c_void_p, c_uint 
from ctypes.wintypes import ULONG, BOOLEAN, BYTE, WORD, DWORD, HANDLE, BOOL, \
        WCHAR, LPWSTR, LPCWSTR
from kernel32_dll_api import CreateFile, close_handle

hid_dll = ctypes.windll.hid
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

class GUID(ctypes.Structure):
    """ 
        Globally Unique Identifier Buffer
        --- 

        Pointer to a caller-allocated GUID buffer 
        that the routine uses to return the device
        interface GUID for HIDClass devices.
        retrieved from https://learn.microsoft.com/ 

    Args:
        ctypes (_type_): Structure data type frm C
    """
    _pack_ = 1
    _fields_ = [
        ("data1", DWORD), # Unsigned 4 bytes or 32 bits of data
        ("data2", WORD), # Unsigned 2 bytes or 16 bits of data 
        ("data3", WORD), 
        ("data4", BYTE * 8),
    ]

class HIDD_ATTRIBUTES(Structure):#NOTE: needed
    _fields_ = [("cb_size", DWORD),
        ("vendor_id", c_ushort),
        ("product_id", c_ushort),
        ("version_number", c_ushort)
    ]

class HIDP_CAPS(Structure):#NOTE NEEDED
    _fields_ = [
        ("usage", c_ushort), #usage id
        ("usage_page", c_ushort), #usage page
        ("input_report_byte_length", c_ushort),
        ("output_report_byte_length", c_ushort),
        ("feature_report_byte_length", c_ushort),
        ("reserved", c_ushort * 17),
        ("number_link_collection_nodes", c_ushort),
        ("number_input_button_caps", c_ushort),
        ("number_input_value_caps", c_ushort),
        ("number_input_data_indices", c_ushort),
        ("number_output_button_caps", c_ushort),
        ("number_output_value_caps", c_ushort),
        ("number_output_data_indices", c_ushort),
        ("number_feature_button_caps", c_ushort),
        ("number_feature_value_caps", c_ushort),
        ("number_feature_data_indices", c_ushort)
    ]

class HIDP_BUTTON_CAPS(Structure):
    class RANGE_NOT_RANGE(Union):
        class RANGE(Structure):
            _fields_ = [
                ("usage_min", c_ushort),     ("usage_max", c_ushort),
                ("string_min", c_ushort),    ("string_max", c_ushort),
                ("designator_min", c_ushort),("designator_max", c_ushort),
                ("data_index_min", c_ushort), ("data_index_max", c_ushort)
            ]

        class NOT_RANGE(Structure):
            _fields_ = [
                ("usage", c_ushort),            ("reserved1", c_ushort),
                ("string_index", c_ushort),      ("reserved2", c_ushort),
                ("designator_index", c_ushort),  ("reserved3", c_ushort),
                ("data_index", c_ushort),        ("reserved4", c_ushort)
            ]
        _fields_ = [
            ("range", RANGE),
            ("not_range", NOT_RANGE)
        ]

    _fields_ = [
        ("usage_page", c_ushort),
        ("report_id", c_ubyte),
        ("is_alias", BOOLEAN),
        ("bit_field", c_ushort),
        ("link_collection", c_ushort),
        ("link_usage", c_ushort),
        ("link_usage_page", c_ushort),
        ("is_range", BOOLEAN),
        ("is_string_range", BOOLEAN),
        ("is_designator_range", BOOLEAN),
        ("is_absolute", BOOLEAN),
        ("reserved", c_ulong * 10),
        ("union", RANGE_NOT_RANGE)
    ]

class HIDP_VALUE_CAPS(Structure):
    class RANGE_NOT_RANGE(Union):
        class RANGE(Structure):
            _fields_ = [
                ("usage_min", c_ushort),     ("usage_max", c_ushort),
                ("string_min", c_ushort),    ("string_max", c_ushort),
                ("designator_min", c_ushort),("designator_max", c_ushort),
                ("data_index_min", c_ushort), ("data_index_max", c_ushort)
            ]

        class NOT_RANGE(Structure):
            _fields_ = [
                ("usage", c_ushort),            ("reserved1", c_ushort),
                ("string_index", c_ushort),      ("reserved2", c_ushort),
                ("designator_index", c_ushort),  ("reserved3", c_ushort),
                ("data_index", c_ushort),        ("reserved4", c_ushort)
            ]
        _fields_ = [
            ("range", RANGE),
            ("not_range", NOT_RANGE)
        ]

    _fields_ = [
        ("usage_page", c_ushort),
        ("report_id", c_ubyte),
        ("is_alias", BOOLEAN),
        ("bit_field", c_ushort),
        ("link_collection", c_ushort),
        ("link_usage", c_ushort),
        ("link_usage_page", c_ushort),
        ("is_range", BOOLEAN),
        ("is_string_range", BOOLEAN),
        ("is_designator_range", BOOLEAN),
        ("is_absolute", BOOLEAN),
        ("has_null", BOOLEAN),
        ("reserved", c_ubyte),
        ("bit_size", c_ushort),
        ("report_count", c_ushort),
        ("reserved2", c_ushort * 5),
        ("units_exp", c_ulong),
        ("units", c_ulong),
        ("logical_min", c_long),
        ("logical_max", c_long),
        ("physical_min", c_long),
        ("physical_max", c_long),
        ("union", RANGE_NOT_RANGE)
    ]

class HIDP_DATA(Structure):
    class HIDP_DATA_VALUE(Union):
        _fields_ = [
            ("raw_value", c_ulong),
            ("on", BOOLEAN),
        ]
    
HidP_Input   = 0x0000
HidP_Output  = 0x0001
HidP_Feature = 0x0002

FACILITY_HID_ERROR_CODE = 0x11
def HIDP_ERROR_CODES(sev, code):
    return (((sev) << 28) | (FACILITY_HID_ERROR_CODE << 16) | (code)) & 0xFFFFFFFF

class HidStatus(object):
    HIDP_STATUS_SUCCESS                  = ( HIDP_ERROR_CODES(0x0, 0) )
    HIDP_STATUS_NULL                     = ( HIDP_ERROR_CODES(0x8, 1) )
    HIDP_STATUS_INVALID_PREPARSED_DATA   = ( HIDP_ERROR_CODES(0xC, 1) )
    HIDP_STATUS_INVALID_REPORT_TYPE      = ( HIDP_ERROR_CODES(0xC, 2) )
    HIDP_STATUS_INVALID_REPORT_LENGTH    = ( HIDP_ERROR_CODES(0xC, 3) )
    HIDP_STATUS_USAGE_NOT_FOUND          = ( HIDP_ERROR_CODES(0xC, 4) )
    HIDP_STATUS_VALUE_OUT_OF_RANGE       = ( HIDP_ERROR_CODES(0xC, 5) )
    HIDP_STATUS_BAD_LOG_PHY_VALUES       = ( HIDP_ERROR_CODES(0xC, 6) )
    HIDP_STATUS_BUFFER_TOO_SMALL         = ( HIDP_ERROR_CODES(0xC, 7) )
    HIDP_STATUS_INTERNAL_ERROR           = ( HIDP_ERROR_CODES(0xC, 8) )
    HIDP_STATUS_I8042_TRANS_UNKNOWN      = ( HIDP_ERROR_CODES(0xC, 9) )
    HIDP_STATUS_INCOMPATIBLE_REPORT_ID   = ( HIDP_ERROR_CODES(0xC, 0xA) )
    HIDP_STATUS_NOT_VALUE_ARRAY          = ( HIDP_ERROR_CODES(0xC, 0xB) )
    HIDP_STATUS_IS_VALUE_ARRAY           = ( HIDP_ERROR_CODES(0xC, 0xC) )
    HIDP_STATUS_DATA_INDEX_NOT_FOUND     = ( HIDP_ERROR_CODES(0xC, 0xD) )
    HIDP_STATUS_DATA_INDEX_OUT_OF_RANGE  = ( HIDP_ERROR_CODES(0xC, 0xE) )
    HIDP_STATUS_BUTTON_NOT_PRESSED       = ( HIDP_ERROR_CODES(0xC, 0xF) )
    HIDP_STATUS_REPORT_DOES_NOT_EXIST    = ( HIDP_ERROR_CODES(0xC, 0x10) )
    HIDP_STATUS_NOT_IMPLEMENTED          = ( HIDP_ERROR_CODES(0xC, 0x20) )

    error_message_dict = {
        HIDP_STATUS_SUCCESS                  : "success",
        HIDP_STATUS_NULL                     : "null",
        HIDP_STATUS_INVALID_PREPARSED_DATA   : "invalid preparsed data",
        HIDP_STATUS_INVALID_REPORT_TYPE      : "invalid report type",
        HIDP_STATUS_INVALID_REPORT_LENGTH    : "invalid report length",
        HIDP_STATUS_USAGE_NOT_FOUND          : "usage not found",
        HIDP_STATUS_VALUE_OUT_OF_RANGE       : "value out of range",
        HIDP_STATUS_BAD_LOG_PHY_VALUES       : "bad log phy values",
        HIDP_STATUS_BUFFER_TOO_SMALL         : "buffer too small",
        HIDP_STATUS_INTERNAL_ERROR           : "internal error",
        HIDP_STATUS_I8042_TRANS_UNKNOWN      : "i8042/I8242 trans unknown",
        HIDP_STATUS_INCOMPATIBLE_REPORT_ID   : "incompatible report ID",
        HIDP_STATUS_NOT_VALUE_ARRAY          : "not value array",
        HIDP_STATUS_IS_VALUE_ARRAY           : "is value array",
        HIDP_STATUS_DATA_INDEX_NOT_FOUND     : "data index not found",
        HIDP_STATUS_DATA_INDEX_OUT_OF_RANGE  : "data index out of range",
        HIDP_STATUS_BUTTON_NOT_PRESSED       : "button not pressed",
        HIDP_STATUS_REPORT_DOES_NOT_EXIST    : "report does not exist",
        HIDP_STATUS_NOT_IMPLEMENTED          : "not implemented"
    }

    def __init__(self, error_code):
        error_code &= 0xFFFFFFFF #NOTE: read how to use `$=` 
        self.error_code = error_code
        if error_code != self.HIDP_STATUS_SUCCESS:
            if error_code in self.error_message_dict:
                raise Exception("hidP error: %s" % self.error_message_dict[error_code])
            else:
                raise Exception("Unknown HidP error (%s)"%hex(error_code))

def get_hid_guid():
    hid_guid = GUID()
    hid_dll.HidD_GetHidGuid(ctypes.byref(hid_guid))
    return hid_guid

class HidDeviceBaseClass(object):
    _raw_reports_lock = threading.Lock()

    def __init__(self) -> None:
        pass

class HidDeviceCreateFile(HidDeviceBaseClass):
    def __init__(self, device_path, instance_id) -> None:
        self.device_path = device_path
        self.instance_id = instance_id
        self.hid_handle = None
        self.preparsed_data = None
        self.__open_status = False
        self.hid_caps = None
        super().__init__()
    
    def open(self):
        hid_handle = CreateFile(
            self.device_path,
            (-2147483648) | (1073741824),
            (1)|(2),
            None,
            3,
            (1073741824) | (128),
            0
        )

        if not hid_handle or hid_handle == INVALID_HANDLE_VALUE:
            raise Exception("Handle could not be created!")
        self.hid_handle = hid_handle
        preparsed_data = ctypes.c_void_p()
        hid_dll.HidD_GetPreparsedData(int(hid_handle), ctypes.byref(preparsed_data))
        if not preparsed_data:
            raise Exception("Failed to get preparsed data!")
        self.preparsed_data = preparsed_data
        self.hid_caps = HIDP_CAPS()
        HidStatus( hid_dll.HidP_GetCaps(self.preparsed_data,
            ctypes.byref(self.hid_caps)) )

      
        caps_length = c_ulong() 

        all_items = [\
            (HidP_Input,   HIDP_BUTTON_CAPS,
                self.hid_caps.number_input_button_caps,
                hid_dll.HidP_GetButtonCaps
            ),
            (HidP_Input,   HIDP_VALUE_CAPS,
                self.hid_caps.number_input_value_caps,
                hid_dll.HidP_GetValueCaps
            ),
            (HidP_Output,  HIDP_BUTTON_CAPS,
                self.hid_caps.number_output_button_caps,
                hid_dll.HidP_GetButtonCaps
            ),
            (HidP_Output,  HIDP_VALUE_CAPS,
                self.hid_caps.number_output_value_caps,
                hid_dll.HidP_GetValueCaps
            ),
            (HidP_Feature, HIDP_BUTTON_CAPS,
                self.hid_caps.number_feature_button_caps,
                hid_dll.HidP_GetButtonCaps
            ),
            (HidP_Feature, HIDP_VALUE_CAPS,
                self.hid_caps.number_feature_value_caps,
                hid_dll.HidP_GetValueCaps
            ),
        ]

        print(self.preparsed_data)
        print("handle created!",close_handle(int(hid_handle)))
            


