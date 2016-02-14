'''
Created on Feb 13, 2016

@author: Chris Wilkerson
'''

from construct import Struct, ULInt8, ULInt24, BitStruct, Enum, BitField, Padding

RPLIDAR_CMD_SYNC_BYTE       = 0XA5
RPLIDAR_CMDFLAG_HAS_PAYLOAD = 0X80

RPLIDAR_ANS_SYNC_BYTE1      = 0XA5
RPLIDAR_ANS_SYNC_BYTE2      = 0X5A

RPLIDAR_ANS_PKTFLAG_LOOP    = 0X1

RPLIDAR_ANS_HEADER_SIZE_MASK     = 0x3FFFFFFF
RPLIDAR_ANS_HEADER_SUBTYPE_SHIFT = 30

rplidar_cmd_format = Struct("cmd_format",
            ULInt8("sync_byte"), # Must be RPLIDAR_CMD_SYNC_BYTE
            ULInt8("cmd_flag")
            )

rplidar_response_header_format = Struct("ans_header",
            ULInt8("sync_byte_1"), # Must be RPLIDAR_ANS_SYNC_BYTE1
            ULInt8("sync_byte_2"), # Must be RPLIDAR_ANS_SYNC_BYTE2
            # _u32 size_q30_subtype; // see _u32 size:30; _u32 subType:2;
            # The size will contain the majority of the bytes, the subtype
            # is only 2 bits with either SINGLE or MULTI response currently available
            ULInt24("size"),
            BitStruct("subtype_mode",
                Enum(BitField("mode", 2), SINGLE = 0x0, MULTI = 0x1, _default_ = "RESERVED"),
                Padding(6)),
            ULInt8("type")                    
            )