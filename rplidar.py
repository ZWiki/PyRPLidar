'''
Created on Feb 13, 2016

@author: Chris Wilkerson
'''

import serial
from rplidar_protocol import *
from rplidar_cmd import *
from construct import Container
import time
from Queue import Queue
from rplidar_types import RPLidarFrame
from rplidar_monitor import RPLidarMonitor

ascii_schematic = r"""
             1
         _________
        /         \
       /    ___    \
      /    /   \    \
  4  |\    \___/    /|  2
     | \           / | 
      \ \_________/ /
       \           /
        \         /
         \_______/

             3             
"""
##
#             1
#         _________
#        /         \
#       /    ___    \
#      /    /   \    \
#  4  |\    \___/    /|   2
#     | \           / | 
#      \ \_________/ /
#       \           /
#        \         /
#         \_______/
#
#             3            
#
# The above is a rough image of the sides of the lidar.
##
class RPLidar(object):
    def __init__(self, port, baudrate=115200, timeout=2, max_size_points=360, max_size_frames=10):
        self.serial_port = None # The actual serial port 
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_connected = False
        self.is_motor_running = False
        self.is_scanning = False
        
        # Raw data
#         self.raw_points = Queue()
#         self.raw_frames = Queue()
#         self.test = Queue()
        
        self._raw_points = list()
        
        # Parsed data
#         self.points = Queue(maxsize=max_size_points)
#         self.frames = Queue(maxsize=max_size_frames)
        
        
#         self.current_frame = RPLidarFrame()
        
        self.rplidar_monitor = None
        
    def connect(self):
        if not self.is_connected:
            try:
                self.serial_port = serial.Serial(port=self.port,
                                                 baudrate=self.baudrate,
                                                 stopbits=serial.STOPBITS_ONE,
                                                 parity=serial.PARITY_NONE,
                                                 timeout=self.timeout
                                                 )
                self.stop_motor()
                self.is_connected = True
            except serial.SerialException as e:
                # TOOD: Handle this 
                print 'error conecting'
                
    def disconnect(self):
        self._stop_monitor()
        self.stop_scan()
        if self.is_connected:
            try:
                if self.rplidar_monitor is not None:
                    self.stop_motor()
                self.serial_port.close()
                self.is_connected = False
            except serial.SerialException as e:
                print e.message

    def start_motor(self):
        self.serial_port.setDTR(False)
        self.is_motor_running = True
        
    def stop_motor(self):
        if self.is_motor_running:
            self.serial_port.setDTR(True)
            self.is_motor_running = False
        
        
    def get_health(self, timeout=2):
        self.serial_port.flushInput()
        
        self._send_command(RPLIDAR_CMD_GET_DEVICE_HEALTH)
        if self._read_response_header(timeout) == RPLIDAR_ANS_TYPE_DEVHEALTH:
            data = self.serial_port.read(rplidar_response_device_health_format.sizeof())
            parsed_data = rplidar_response_device_health_format.parse(data)
            return {
                    "status" : parsed_data.status,
                    "error_code" : parsed_data.error_code
                    }
        else:
            pass
            #TODO: raise an exception
            
    def get_device_info(self, timeout=2):
        if not self.is_connected:
            pass
            # TODO: Throw an exception
            
        self.is_scanning = False
        self.serial_port.flushInput()
        
        self._send_command(RPLIDAR_CMD_GET_DEVICE_INFO)
        if self._read_response_header(timeout) == RPLIDAR_ANS_TYPE_DEVINFO:
            data = self.serial_port.read(rplidar_response_device_info_format.sizeof())
            parsed_data = rplidar_response_device_info_format.parse(data)
            return {
                    "model" : parsed_data.model,
                    "firmware_version_major" : parsed_data.firmware_major,
                    "firmware_version_minor" : parsed_data.firmware_minor,
                    "hardware_version" : parsed_data.hardware,
                    "serial_number" : to_hex(parsed_data.serial_number)
                }
        else:
            pass
        # TODO: exception
        
    def start_scan(self):
        self.rplidar_monitor = RPLidarMonitor(self)
        self.rplidar_monitor.start()
        
    def stop_scan(self):
        self._send_command(RPLIDAR_CMD_STOP)
        self.stop_motor()
        time.sleep(0.2)
        
        
    def _send_command(self, command):
        # Build the command from the command format
        data = rplidar_cmd_format.build(Container(
                                sync_byte=RPLIDAR_CMD_SYNC_BYTE, cmd_flag=command))
        self.serial_port.write(data)
        
        
    def _read_response_header(self, timeout=2):
        start = time.time()
        
        # Keep trying until the timeout is reached
        while time.time() < start + timeout:
            # If the number of bytes in the input buffer is less than
            # the expected bytes from the response header, then we need to wait
            if self.serial_port.inWaiting() < rplidar_response_header_format.sizeof():
                time.sleep(0.010) # Wait 10ms and try again
            else:
                data = self.serial_port.read(rplidar_response_header_format.sizeof())
                parsed_data = rplidar_response_header_format.parse(data)
                if(parsed_data.sync_byte_1 != RPLIDAR_ANS_SYNC_BYTE1 or
                   parsed_data.sync_byte_2 != RPLIDAR_ANS_SYNC_BYTE2):
                    pass
                    # TODO: Raise an exception
                else:
                    return parsed_data.type
                    
        # TODO: Raise exception if we get here
                
            
    def _stop_scan(self):
        if not self.is_connected:
            pass
            # TODO: exception
        if not self.is_scanning:
            return
        
        self.stop_motor()
        self._send_command(RPLIDAR_CMD_STOP)
        time.sleep(0.1)
        
    def _stop_monitor(self):
        if self.rplidar_monitor is not None:
            self.rplidar_monitor.join()
            self.rplidar_monitor = None
        
    
to_hex = lambda x:"".join([hex(ord(c))[2:].zfill(2) for c in x])
        