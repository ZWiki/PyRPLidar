'''
Created on Feb 13, 2016

@author: Chris Wilkerson
'''

from rplidar import RPLidar, ascii_schematic
from rplidar_types import RPLidarPoint
import time
import matplotlib.pyplot as plt
import numpy as np
import random
import argparse
from argparse import RawTextHelpFormatter

# Parsing stuff
parser = argparse.ArgumentParser(description="A tool for debugging/visualizing RPLidar",
                                 formatter_class=RawTextHelpFormatter)
args = None
angle_adjust = 90

# Plotting stuff
fig = plt.figure(figsize=(6,6), dpi=100)
radius_view = plt.Circle((0, 0), 6000, color='r', fill=False)
roomba = plt.Circle((0,0), 100, color='y', fill=True)
ax = fig.add_subplot(111)

def parse_args():
    global args, angle_adjust
    parser.add_argument("-c", "--cross-hairs", type=str, nargs="?", required=False,
                        help="\
The number of cross-hair segments to have. Can either be\n\
a number, i.e.\n\
5 -- create 5 equally spaced segments, or a degree, i.e.\n\
90d -- create a segment every 90 degrees",
                        default=4)
    
    parser.add_argument("-f", "--front", type=int, nargs="?", required=False,
                        choices=range(1,5),
                        help="\
%s\n\n\
Which direction you would like to consider the 'front'" % ascii_schematic,
                        default=1)
    
    parser.add_argument("-d", "--dpi", type=int, nargs="?", required=False,
                        help="The dpi to graph with.",
                        default=None) #TODO: Make this a value

    parser.add_argument("-l", "--plot-lines", type=bool, nargs="?", required=False,
                        help="\
Whether or not to plot the examples with lines.\n\
This may help to better visualize certain areas than simply\
using points",
                        default=False)
    
    parser.add_argument("-p", "--port-name", type=str, required=True,
                        help="The name of the port that RPLidar is connected to")

    args = parser.parse_args()
    print dir(args)
    # By default 4 faces the front, i.e. is on top. Becaue of that
    # the values were assigned in such a way that I can now just rotate
    # by a multiple of 90 degrees CCW
    angle_adjust = (args.front*90)%360
        

def get_cross_hairs():
    """
    Return the cross-hairs in degrees
    """
    
    try:
        cross_hairs = int(args.cross_hairs)
        if cross_hairs == 0:
            return None
        else:
            return 360.0/cross_hairs
    except ValueError:
        return int(args.cross_hairs[:-1])
        if cross_hairs == 0:
            return None
    
def rotate_point(x, y, angle, x_origin=0, y_origin=0):
    new_x = (x - x_origin)*np.cos(angle*np.pi/180.0)
    new_y = (y - y_origin)*np.sin(angle*np.pi/180.)
    return new_x, new_y

def set_plot(x_y = None):
    x = np.array(range(-6000,7000,1000))
    y = np.array(range(-6000,7000,1000))
    plt.xticks(x, range(-6,7))
    plt.yticks(y, range(-6,7))
    
    # Add some labels
    plt.xlabel("X-Location (meters)")
    plt.ylabel("Y-Location (meters)")
    
    # Plot radius circles every 1m
    for radius in range(1000, 6000, 1000):
        c = plt.Circle((0,0), radius, color='gray', fill=False)
        ax.add_patch(c)
        
    # Add cross hairs for the graph
    cross_hairs = get_cross_hairs()
    if cross_hairs:
        r = np.arange(0, 180, get_cross_hairs())
        for angle in r:
#             angle = (angle+angle_adjust)%360 # Adjust if necessary
            x1 = np.cos(angle*(np.pi/180))*6000
            x2 = -x1
            y1 = np.sin(angle*(np.pi/180))*6000
            y2 = -y1
            
            ax.plot((x1, x2), (y1, y2), color='gray')
            ax.text(x1, y1, str(angle))
            ax.text(x2, y2, str((angle+180)%360.0))  
        
    ax.add_patch(radius_view)
    ax.add_patch(roomba)
    
    # TODO: Something is screwy with the x and y coords. The below code works
    # but there should be a default where there is no need to adjust x and y.
    # I'm thinking that x may not be equivalent to cos and y to sin in this
    # lidar model
    if x_y is not None:
        if args.front == 1:
            ax.plot(x_y[1], x_y[0], '-' if args.plot_lines else 'o')
        elif args.front == 2:
            ax.plot([-1*(x) for x in x_y[0]], x_y[1], '-' if args.plot_lines else 'o')
        elif args.front == 3:
            ax.plot([-1*(y) for y in x_y[1]], [-1*(x) for x in x_y[0]], '-' if args.plot_lines else 'o')
        elif args.front == 4:
            ax.plot(x_y[0], [-1*(y) for y in x_y[1]], '-' if args.plot_lines else 'o')
#         else:
#             ax.plot(x_y[0], x_y[1], 'o') # This is just for debugging what is wrong with the above TODO
        
if __name__ == '__main__':
    parse_args()
    print args.front, type(args.front)
    lidar = RPLidar(args.port_name)
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
#                     x_comp = point.distance * np.sin(point.angle*np.pi/180)
#                     y_comp = point.distance * np.cos(point.angle*np.pi/180)
                    _x.append(x_comp)
                    _y.append(y_comp)
#                 print "Angle: %.2f    Dist: %.2f    Q: %d" % (point.angle, point.distance, point.quality)
            set_plot((_x, _y))
            plt.axis('equal')
            plt.pause(0.15)
            plt.cla()
#             time.sleep(0.15)
    except Exception as e:
        pass
      
#     lidar.disconnect()

        

        
        
