'''
Created on Feb 13, 2016

@author: Chris Wilkerson
'''

from construct import Struct, ULInt8, ULInt16, String, Byte, Enum, BitStruct, BitField, Flag, Const
# Commands without payload response
RPLIDAR_CMD_STOP       = 0x25
RPLIDAR_CMD_SCAN       = 0X20
RPLIDAR_CMD_FORCE_SCAN = 0X21
RPLIDAR_CMD_RESET      = 0X40

# Commands without payload but have response
RPLIDAR_CMD_GET_DEVICE_INFO   = 0x50
RPLIDAR_CMD_GET_DEVICE_HEALTH = 0x52


# Response
RPLIDAR_ANS_TYPE_MEASUREMENT = 0x81
RPLIDAR_ANS_TYPE_DEVINFO     = 0x4
RPLIDAR_ANS_TYPE_DEVHEALTH   = 0x6
RPLIDAR_STATUS_OK            = 0x0
RPLIDAR_STATUS_WARNING       = 0x1
RPLIDAR_STATUS_ERROR         = 0x2

RPLIDAR_RESP_MEASUREMENT_SYNCBIT       = 0x1<<0
RPLIDAR_RESP_MEASUREMENT_QUALITY_SHIFT = 2
RPLIDAR_RESP_MEASUREMENT_CHECKBIT      = 0x1<<0
RPLIDAR_RESP_MEASUREMENT_ANGLE_SHIFT   = 1

## 
#As defined by Figure 9. in "rplidar_interface_protocol_en.pdf"
##
rplidar_response_device_measurement_format = Struct("measurement_format",
        BitStruct("byte0",
                  BitField("quality", 6),
                  Flag("syncbit_inverse"),
                  Flag("syncbit")
        ),
        BitStruct("byte1",
                  BitField("angle_low", 7),
                  Const(Flag("check_bit"), 1) # Must be set to 1
        ),
        ULInt8("angle_high"),
        ULInt16("distance_q2")
)

##
# As defined by Figure 12. in "rplidar_interface_protocol_en.pdf"
##
rplidar_response_device_info_format = Struct("info_format",
        ULInt8("model"),
        ULInt8("firmware_minor"),
        ULInt8("firmware_major"),
        ULInt8("hardware"),
        String("serial_number", 16)
)

##
# As defined by Figure 14. in "rplidar_interface_protocol_en.pdf"
##
rplidar_response_device_health_format = Struct("health_format",
        Enum(Byte("status"),
             RPLIDAR_STATUS_OK = RPLIDAR_STATUS_OK,
             RPLIDAR_STATUS_WARNING = RPLIDAR_STATUS_WARNING,
             RPLIDAR_STATUS_ERROR = RPLIDAR_STATUS_ERROR),
        ULInt16("error_code")
)

