'''
Created on Feb 13, 2016

@author: Chris Wilkerson
'''

from rplidar import RPLidar
from rplidar_types import RPLidarPoint
import time
import matplotlib.pyplot as plt
import numpy as np
import random

fig = plt.figure(figsize=(6,6), dpi=160)
radius_view = plt.Circle((0, 0), 6000, color='r', fill=False)
roomba = plt.Circle((0,0), 100, color='y', fill=True)
ax = fig.add_subplot(111)

def set_plot(x_y = None):
    x = np.array(range(-6000,7000,1000))
    y = np.array(range(-6000,7000,1000))
    plt.xticks(x, range(-6,7))
    plt.yticks(y, range(-6,7))
    
    # Add some labels
    plt.xlabel("X-Location (meters)")
    plt.ylabel("Y-Location (meters)")
    ax.add_patch(radius_view)
    ax.add_patch(roomba)
    
    if x_y is not None:
        ax.plot(x_y[0], x_y[1], 'o')

if __name__ == '__main__':
    lidar = RPLidar('/dev/ttyUSB0')
    lidar.connect()
    print lidar.get_health()
    print lidar.get_device_info()
      
    lidar.start_scan()
    time.sleep(2) # Let that baby warm up
    
    set_plot()
    plt.ion()
    plt.show()
    
    try:
        while True:
            point_list = [p for p in lidar._raw_points]
            rp_point_list = [RPLidarPoint(raw_point) for raw_point in point_list]
            rp_point_list.sort(key = lambda v: v.angle)
            _x = []
            _y = []
            for point in rp_point_list:
                # Only take the good quality points
                if point.quality > 0 and abs(point.distance<=6000):
                    x_comp = point.distance * np.cos(point.angle * (np.pi/180))
                    y_comp = point.distance * np.sin(point.angle * (np.pi/180))
#                     x_comp = point.distance * np.sin(point.angle)
#                     y_comp = point.distance * np.cos(point.angle)
                    _x.append(x_comp)
                    _y.append(y_comp)
#                 print "Angle: %.2f    Dist: %.2f    Q: %d" % (point.angle, point.distance, point.quality)
            set_plot((_x, _y))
            plt.axis('equal')
            plt.pause(0.1)
            plt.cla()
            time.sleep(0.15)
    except Exception as e:
        pass
      
    lidar.disconnect()

        

        
        
