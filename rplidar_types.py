'''
Created on Feb 13, 2016

@author: Chris Wilkerson
'''
from collections import deque
from rplidar_cmd import *

class RPLidarRawFrame(object):
    def __init__(self):
        self.raw_points = list()
    
    def add_raw_point(self, raw_point):
        self.raw_points.append(raw_point)
        
class RPLidarFrame(object):
    def __init__(self, max_len=360):
        self.angle = deque(maxlen=max_len)
        self.distance = deque(maxlen=max_len)
    
    def add_point(self, point):
        pass
    
class RPLidarPoint(object):
    def __init__(self, raw_point):
        self.raw_point = raw_point
        parsed_point = rplidar_response_device_measurement_format.parse(self.raw_point)
        self.syncbit = parsed_point.byte0.syncbit
        self.syncbit_inverse = parsed_point.byte0.syncbit_inverse
        self.quality = parsed_point.byte0.quality
        self.check_bit = parsed_point.byte1.check_bit
        self.angle = ((parsed_point.angle_high << 7) | parsed_point.byte1.angle_low)/64.0
        self.distance = parsed_point.distance_q2/4.0