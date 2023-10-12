import sys
import ctypes
import collections
import threading
from ctypes import Structure, Union, c_ubyte, c_long, c_ulong, c_ushort, \
        c_wchar, c_void_p, c_uint 
from ctypes.wintypes import ULONG, BOOLEAN, BYTE, WORD, DWORD, HANDLE
from kernel32_dll_api import CreateFile, close_handle 

hid_dll = ctypes.windll.hid
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
if sys.version_info >= (3,):
    import winreg
else:
    import _winreg as winreg

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

class HIDD_ATTRIBUTES(Structure):
    _fields_ = [("cb_size", DWORD),
        ("vendor_id", c_ushort),
        ("product_id", c_ushort),
        ("version_number", c_ushort)
    ]

class HIDP_CAPS(Structure):
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

class OVERLAPPED(Structure):
    class OFFSET_OR_HANDLE(Union):
        class OFFSET(Structure):
            _fields_ = [
                ("offset",      DWORD),
                ("offset_high", DWORD) ]

        _fields_ = [
                ("offset",      OFFSET),
                ("pointer",     c_void_p) ]
    _fields_ = [
        ("internal",        ctypes.POINTER(ULONG)),
        ("internal_high",   ctypes.POINTER(ULONG)),
        ("u",               OFFSET_OR_HANDLE),
        ("h_event",         HANDLE)
    ]
    
class ReadOnlyList(collections.UserList):
    "Read only sequence wrapper"
    def __init__(self, any_list):
        collections.UserList.__init__(self, any_list)
    def __setitem__(self, index, value):
        raise ValueError("Object is read-only")
    
HidP_Input   = 0x0000
HidP_Output  = 0x0001
HidP_Feature = 0x0002

FACILITY_HID_ERROR_CODE = 0x11
def HIDP_ERROR_CODES(sev, code):
    return (((sev) << 28) | (FACILITY_HID_ERROR_CODE << 16) | (code)) & 0xFFFFFFFF
def get_full_usage_id(page_id, usage_id):
    """Convert to composite 32 bit page and usage ids"""
    return (page_id << 16) | usage_id
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
        error_code &= 0xFFFFFFFF 
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

        #initialize hardware related vars
        self.__button_caps_storage     = list()
        self.report_set                = dict()
        self.__reading_thread          = None
        self.__input_processing_thread = None
        self._input_report_queue       = None
        self.hid_caps                  = None
        self.ptr_preparsed_data        = None
        self.hid_handle                = None
        self.usages_storage            = dict()

        self.device_path        = device_path
        self.instance_id        = instance_id
        self.product_name       = ""
        self.vendor_name        = ""
        self.serial_number      = ""
        self.vendor_id          = 0
        self.product_id         = 0
        self.version_number     = 0
        HidDeviceBaseClass.__init__(self)

        # HID device handle first
        h_hid = INVALID_HANDLE_VALUE
        try:
            h_hid = int( CreateFile(device_path,
                        (-2147483648) | (1073741824),
                        (1)|(2),
                        None,
                        3,
                        (1073741824) | (128),
                        0)
                )
        except:
            pass

        if h_hid == INVALID_HANDLE_VALUE:
            return

        try:
            # get device attributes
            hidd_attributes = HIDD_ATTRIBUTES() 
            hidd_attributes.cb_size = ctypes.sizeof(hidd_attributes)
            if not hid_dll.HidD_GetAttributes(h_hid, ctypes.byref(hidd_attributes)):
                del hidd_attributes
                return #can't read attributes

            #set local references
            self.vendor_id  = hidd_attributes.vendor_id
            self.product_id = hidd_attributes.product_id
            self.version_number = hidd_attributes.version_number
            del hidd_attributes

            # manufacturer string
            vendor_string_type = c_wchar * 128
            vendor_name = vendor_string_type()
            if not hid_dll.HidD_GetManufacturerString(h_hid,
                    ctypes.byref(vendor_name),
                    ctypes.sizeof(vendor_name)) or not len(vendor_name.value):
                self.vendor_name = "Unknown manufacturer"
            else:
                self.vendor_name = vendor_name.value
            del vendor_name
            del vendor_string_type

            # string buffer for product string
            product_name_type = c_wchar * 128
            product_name = product_name_type()
            if not hid_dll.HidD_GetProductString(h_hid,
                        ctypes.byref(product_name),
                        ctypes.sizeof(product_name)) or not len(product_name.value):
                # alternate method, refer to windows registry for product
                # information
                path_parts = device_path[len("\\\\.\\"):].split("#")
                h_register = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                    "SYSTEM\\CurrentControlSet\\Enum\\" + \
                    path_parts[0] + "\\" + \
                    path_parts[1] + "\\" + \
                    path_parts[2] )
                self.product_name, other = winreg.QueryValueEx(h_register,
                        "DeviceDesc")
                winreg.CloseKey(h_register)
            else:
                self.product_name = product_name.value
            del product_name
            del product_name_type

            # serial number string
            serial_number_string = c_wchar * 64
            serial_number = serial_number_string()
            if not hid_dll.HidD_GetSerialNumberString(h_hid,
                    ctypes.byref(serial_number),
                    ctypes.sizeof(serial_number)) or not len(serial_number.value):
                self.serial_number = ""
            else:
                self.serial_number = serial_number.value
            del serial_number
            del serial_number_string
        finally:
            # clean up
            close_handle(h_hid)

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

        for report_kind, struct_kind, max_items, get_control_caps in all_items:
            if not int(max_items):
                continue 

            ctrl_array_type = struct_kind * max_items
            ctrl_array_struct = ctrl_array_type()

            caps_length.value = max_items
            HidStatus( get_control_caps(\
                report_kind,
                ctypes.byref(ctrl_array_struct),
                ctypes.byref(caps_length),
                self.preparsed_data) )
            #keep reference of usages
            for idx in range(caps_length.value):
                usage_item = HidPUsageCaps( ctrl_array_struct[idx] )
                #by report type
                if report_kind not in self.usages_storage:
                    self.usages_storage[report_kind] = list()
                self.usages_storage[report_kind].append( usage_item )
                #also add report_id to known reports set
                if report_kind not in self.report_set:
                    self.report_set[report_kind] = set()
                self.report_set[report_kind].add( usage_item.report_id )
            del ctrl_array_struct
            del ctrl_array_type # stop

        self.__open_status = True


    def send_feature_report(self, data):
        """Send input/output/feature report ID = report_id, data should be a
        c_byte object with included the required report data
        """
        assert( self.is_opened() )
        #make sure we have c_ubyte array storage
        if not ( isinstance(data, ctypes.Array) and issubclass(data._type_,
                c_ubyte) ):
            raw_data_type = c_ubyte * len(data)
            raw_data = raw_data_type()
            for index in range( len(data) ):
                raw_data[index] = data[index]
        else:
            raw_data = data

        return hid_dll.HidD_SetFeature(int(self.hid_handle),ctypes.byref(raw_data),
                len(raw_data))

    def __reset_vars(self):
        """Reset vars (for init or gc)"""
        self.__button_caps_storage = list()
        self.usages_storage = dict()
        self.report_set = dict()
        self.ptr_preparsed_data = None
        self.hid_handle = None

        self.__reading_thread = None
        self.__input_processing_thread = None
        self._input_report_queue = None


    def is_opened(self):
        """Check if device path resource open status"""
        return self.__open_status

    def close(self):
        """Release system resources"""
        # free parsed data
        if not self.is_opened():
            return
        self.__open_status = False

        # abort all running threads first
        if self.__reading_thread and self.__reading_thread.is_alive():
            self.__reading_thread.abort()

        #avoid posting new reports
        if self._input_report_queue:
            self._input_report_queue.release_events()

        if self.__input_processing_thread and \
                self.__input_processing_thread.is_alive():
            self.__input_processing_thread.abort()

        #properly close API handlers and pointers
        if self.ptr_preparsed_data:
            ptr_preparsed_data = self.ptr_preparsed_data
            self.ptr_preparsed_data = None
            hid_dll.HidD_FreePreparsedData(ptr_preparsed_data)

        # wait for the reading thread to complete before closing device handle
        if self.__reading_thread:
            self.__reading_thread.join()

        if self.hid_handle:
            close_handle(self.hid_handle)

        # make sure report procesing thread is closed
        if self.__input_processing_thread:
            self.__input_processing_thread.join()

        #reset vars (for GC)
        button_caps_storage = self.__button_caps_storage
        self.__reset_vars()

        while button_caps_storage:
            item = button_caps_storage.pop()
            del item

    def __find_reports(self, report_type, usage_page, usage_id = 0):
        "Find input report referencing HID usage control/data item"
        if not self.is_opened():
            raise Exception("Device must be opened")
        #
        results = list()
        if usage_page:
            for report_id in self.report_set.get( report_type, set() ):
                #build report object, gathering usages matching report_id
                report_obj = HidReport(self, report_type, report_id)
                if get_full_usage_id(usage_page, usage_id) in report_obj:
                    results.append( report_obj )
        else:
            #all (any one)
            for report_id in self.report_set.get(report_type, set()): 
                report_obj = HidReport(self, report_type, report_id)
                results.append( report_obj )
        return results

    def find_output_reports(self, usage_page = 0, usage_id = 0):
        "Find output report referencing HID usage control/data item"
        return self.__find_reports(HidP_Output, usage_page, usage_id)

    def find_feature_reports(self, usage_page = 0, usage_id = 0):
        "Find feature report referencing HID usage control/data item"
        return self.__find_reports(HidP_Feature, usage_page, usage_id)

class HidPUsageCaps(object):
    def __init__(self, caps):
        self.report_id = 0

        for fname, ftype in caps._fields_:
            if fname.startswith('reserved'):
                continue
            if fname == 'union':
                continue
            setattr(self, fname, int(getattr(caps, fname)))
        if caps.is_range:
            range_struct = caps.union.range
        else:
            range_struct = caps.union.not_range
        for fname, ftype in range_struct._fields_:
            if fname.startswith('reserved'):
                continue
            if fname == 'union':
                continue
            setattr(self, fname, int(getattr(range_struct, fname)))
        self.is_value  = False
        self.is_button = False
        if isinstance(caps,  HIDP_BUTTON_CAPS):
            self.is_button = True
        elif isinstance(caps, HIDP_VALUE_CAPS):
            self.is_value = True
        else:
            pass


class HidReport(object):
    """This class interfaces an actual HID physical report, providing a wrapper
    that exposes specific usages (usage page and usage ID) as a usage_id value
    map (dictionary).

    """
    def __init__(self, hid_object, report_type, report_id):
        hid_caps = hid_object.hid_caps
        if report_type == HidP_Input:
            self.__raw_report_size = hid_caps.input_report_byte_length
        elif report_type == HidP_Output:
            self.__raw_report_size = hid_caps.output_report_byte_length
        elif report_type == HidP_Feature:
            self.__raw_report_size = hid_caps.feature_report_byte_length
        else:
            raise Exception("Unsupported report type")
        self.__report_kind = report_type  #target report type
        self.__value_array_items = list() #array of usages items
        self.__hid_object = hid_object      #parent hid object
        self.__report_id = c_ubyte(report_id)  #target report Id
        self.__items = dict()       #access items by 'full usage' key
        self.__idx_items = dict()  #access internal items by HID DLL usage index
        self.__raw_data = None       #buffer storage (if needed)
        # build report items list, browse parent hid object for report items
        for item in hid_object.usages_storage.get(report_type, []):
            if item.report_id == report_id:
                if not item.is_range:
                    #regular 'single' usage
                    report_item = ReportItem(self, item)
                    self.__items[report_item.key()] = report_item
                    self.__idx_items[report_item.data_index] = report_item
                    #item is value array?
                    if report_item.is_value_array():
                        self.__value_array_items.append(report_item)
                else:
                    for usage_id in range(item.usage_min,
                            item.usage_max+1):
                        report_item =  ReportItem(self, item, usage_id)
                        self.__items[report_item.key()] = report_item
                        self.__idx_items[report_item.data_index] = report_item


    def __alloc_raw_data(self, initial_values=None):
        """Pre-allocate re-usagle memory"""
        #allocate c_ubyte storage
        if self.__raw_data == None: #first time only, create storage
            raw_data_type = c_ubyte * self.__raw_report_size
            self.__raw_data = raw_data_type()
        elif initial_values == self.__raw_data:
            # already
            return
        else:
            #initialize
            ctypes.memset(self.__raw_data, 0, len(self.__raw_data))
        if initial_values:
            for index in range(len(initial_values)):
                self.__raw_data[index] = initial_values[index]

    def send(self, raw_data = None):
        """Prepare HID raw report (unless raw_data is provided) and send
        it to HID device
        """
        if self.__report_kind != HidP_Output \
                and self.__report_kind != HidP_Feature:
            raise Exception("Only for output or feature reports")
        #valid length
        if raw_data and (len(raw_data) != self.__raw_report_size):
            raise Exception("Report size has to be %d elements (bytes)" \
                % self.__raw_report_size)
        #should be valid report id
        if raw_data and raw_data[0] != self.__report_id.value:
            #hint, raw_data should be a plain list of integer values
            raise Exception("Not matching report id")
        #
        if self.__report_kind != HidP_Output and \
                self.__report_kind != HidP_Feature:
            raise Exception("Can only send output or feature reports")
        #
        elif not ( isinstance(raw_data, ctypes.Array) and \
                issubclass(raw_data._type_, c_ubyte) ):
            # pre-memory allocation for performance
            self.__alloc_raw_data(raw_data)
        #reference proper object
        raw_data = self.__raw_data
        if self.__report_kind == HidP_Output:
            return self.__hid_object.send_output_report(raw_data)
        elif self.__report_kind == HidP_Feature:
            return self.__hid_object.send_feature_report(raw_data) 
        else:
            pass #can't get here (yet)

class ReportItem(object):
    """Represents a single usage field in a report."""
    def __init__(self, hid_report, caps_record, usage_id = 0):
        # from here we can get the parent hid_object
        self.hid_report = hid_report
        self.__is_value  = caps_record.is_value
        self.__is_value_array = bool(self.__is_value and \
            caps_record.report_count > 1)
        if not caps_record.is_range:
            self.usage_id = caps_record.usage
        else:
            self.usage_id = usage_id
        self.page_id = caps_record.usage_page
        if caps_record.is_range:
            #reference to usage within usage range
            offset = usage_id - caps_record.usage_min 
            self.data_index = caps_record.data_index_min + offset
            self.string_index = caps_record.string_min + offset
            self.designator_index = caps_record.designator_min + offset
        else:
            #straight reference
            self.data_index = caps_record.data_index
            self.string_index = caps_record.string_index
            self.designator_index = caps_record.designator_index
        #verify it item is value array
        if self.__is_value:
            if self.__is_value_array:
                byte_size = int((caps_record.bit_size * caps_record.report_count)//8)
                if (caps_record.bit_size * caps_record.report_count) % 8:
                    # TODO: This seems not supported by Windows
                    byte_size += 1


    def key(self):
        "returns unique usage page & id long value"
        return (self.page_id << 16) | self.usage_id

    def is_value_array(self): 
        """Validate if usage was described as value array"""
        return self.__is_value_array
