'''
Created on Feb 13, 2016

@author: Chris Wilkerson
'''

import threading
from rplidar import *
from rplidar_cmd import *
import random
from rplidar_types import *

class RPLidarMonitor(threading.Thread):
    def __init__(self, rplidar):
        threading.Thread.__init__(self)
        self.BYTES_TO_READ = 5
        self.name = "rplidar_monitor"
        self.rplidar = rplidar
        self.alive = threading.Event()
        self.alive.set()
        self.setDaemon(True)
        
        
    def start_scan(self):
        self.rplidar.start_motor()
        self.rplidar._send_command(RPLIDAR_CMD_SCAN)
        if self.rplidar._read_response_header() != RPLIDAR_ANS_TYPE_MEASUREMENT:
            raise Exception("Errrrrr")
        
        
        
    def run(self):
        
        self.start_scan()
        
        _list = []
        _size = 0
        
#         raw_frame = None
        self.rplidar.test = str(random.randint(0, 20))
        while self.alive.isSet():
            if _size == 720:
                self.rplidar._raw_points = _list
                _list = []
                _size = 0
                
            while self.rplidar.serial_port.inWaiting() < self.BYTES_TO_READ:
                time.sleep(0.0001)
            
            raw_point = self.rplidar.serial_port.read(self.BYTES_TO_READ)
#             point = rplidar_response_device_measurement_format.parse(raw_point)
            
            # Add the raw point
            _list.append(raw_point)
            _size += 1

            # When the syncbit == True it means we have a new frame
            # If we had an old raw frame then we save it and continue
#             if point.byte0.syncbit:
#                 if raw_frame is not None:
#                     self.rplidar.raw_frames.put(raw_frame)
#                     
#                 raw_frame = RPLidarRawFrame()
#                 
#             raw_frame.add_raw_point(raw_point)
#             self.rplidar.current_frame.add_point(point)
            
    def join(self, timeout=0.1):
        self.alive.clear()
        self.rplidar._stop_scan()
        threading.Thread.join(self, timeout)
        
