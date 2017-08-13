#! /usr/bin/env python

import rospy
from sensor_msgs.msg import Image
import cv2, cv_bridge
import time
from sensor_msgs.msg import PointCloud2
from sensor_msgs import point_cloud2
import numpy as np
import sys

rospy.init_node('test_node')
# name = sys.argv

dp_im = rospy.wait_for_message('/camera/depth/image_raw', Image)
c_im = rospy.wait_for_message('/camera/rgb/image_raw', Image)
clouds = rospy.wait_for_message('/camera/depth/points', PointCloud2)

b = cv_bridge.CvBridge()

im_d = b.imgmsg_to_cv2(dp_im, desired_encoding='passthrough')
im_c = b.imgmsg_to_cv2(c_im, desired_encoding='bgr8')

print type(im_d)
# print type(im_c)

timestr = time.strftime("%Y%m%d-%H%M%S")

c_filename = 'color_image'+timestr+'.png'
d_filename = 'depth_image'+timestr+'.png'
pc_filename = 'point_cloud'+timestr+'.txt'

cv2.imwrite(c_filename, im_c)
cv2.imwrite(d_filename, im_d)
#cv2.waitKey(0)
#np.savetxt('sample_depth_image', im)

p = np.empty((im_d.shape[0]*im_d.shape[1], 3))
i = 0
for pts in point_cloud2.read_points(clouds, skip_nans=True):
    p[i, 0] = pts[0]
    p[i, 1] = pts[1]
    p[i, 2] = pts[2]
    i += 1

print(p.dtype)
np.savetxt(pc_filename, p)