#! /usr/bin/env python

import rospy
from tf.broadcaster import TransformBroadcaster
from tf.transformations import quaternion_from_euler
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion
from sensor_msgs.msg import Imu
from std_msgs.msg import Int16
from mbot_pointer.msg import Encoder
from math import pi, atan2, sin, cos

from config import count2dis, wheelbase

base_frame_id = '/base_link'
odom_frame_id = '/odom'


class ImuOdom:
    def __init__(self):
        rospy.init_node('imu_odom')

        self.x = 0
        self.y = 0
        self.th = 0
        self.v = 0
        self.w = 0

        self.then = rospy.Time.now()
        self.dt = 0

        rospy.Subscriber('imu_raw', Imu, self.imu_callback)
        self.odom_pub = rospy.Publisher('imu_odom', Odometry, queue_size=5)

    def imu_callback(self,msg):
        pass

    def update(self):
        pass

    def spin(self):
        while not rospy.is_shutdown():
            self.update()


class EncOdom:
    def __init__(self):
        self.x = 0      # X position in planar ground
        self.y = 0      # Y position in planar ground
        self.th = 0     # direction in planar ground
        self.v = 0      # linear velocity
        self.w = 0      # angular velocity

        self.dt = 0

        self.disL = 0
        self.disR = 0
        self.time_cur = 0
        self.time_last = 0

        self.new_message = False
        rospy.Subscriber('encoder', Encoder, self.enc_callback)
        self.odom_pub = rospy.Publisher('enc_odom', Odometry, queue_size=5)
        self.odomBroadcaster = TransformBroadcaster()

    def enc_callback(self,msg):
        self.time_cur = msg.header.stamp.to_sec()
        self.disL = msg.left * count2dis
        self.disR = msg.right * count2dis

        self.update()


    def update(self):
        if self.time_last != 0:
            self.dt = self.time_cur - self.time_last
            trv_dis = (self.disL + self.disR) / 2
            trv_rot = atan2((self.disR - self.disL), wheelbase)
            self.th = self.th + trv_rot
            self.x = self.x + trv_dis * cos(self.th)
            self.y = self.y + trv_dis * sin(self.th)


            self.v = trv_dis / self.dt
            self.w = trv_rot / self.dt

            quaternion = Quaternion()
            quaternion.w = cos(self.th / 2)
            quaternion.z = sin(self.th / 2)

            now = rospy.Time.now()
            odom_msg = Odometry()
            odom_msg.header.stamp = now
            odom_msg.header.frame_id = odom_frame_id
            odom_msg.child_frame_id = base_frame_id
            odom_msg.pose.pose.position.x = self.x
            odom_msg.pose.pose.position.y = self.y
            odom_msg.pose.pose.orientation = quaternion
            odom_msg.twist.twist.linear.x = self.v
            odom_msg.twist.twist.angular.z = self.w

            self.odom_pub.publish(odom_msg)
            self.odomBroadcaster.sendTransform((self.x, self.y, 0),
                                               quaternion_from_euler(0, 0, self.th),
                                               now,
                                               base_frame_id,
                                               odom_frame_id)

        self.time_last = self.time_cur


if __name__ == '__main__':
    rospy.init_node('odom_test')
    try:
        enc_odom = EncOdom()
    except rospy.ROSInterruptException:
        pass
    rospy.spin()
