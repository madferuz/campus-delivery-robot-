#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gps_simulator_node.py
=====================
Owner: Member 3 (Localization & TF).

ROS function #1 for Member 3: a Publisher node that simulates a NEO-6M
style GPS receiver by converting the robot's pose (from /odom) into a
NavSatFix message with realistic Gaussian noise.

Why simulate?
    The TurtleBot3 Gazebo sim does not ship with a GPS plugin out of
    the box. Rather than modify the URDF, we synthesise a GPS fix from
    the existing /odom topic. This is enough to demonstrate every GPS
    use-case in the project (display on RViz, feed into the navigation
    workflow, log in rosbag) without touching the robot description.

Topics:
    Subscribes : /odom                  (nav_msgs/Odometry)
    Publishes  : /delivery/gps/fix      (sensor_msgs/NavSatFix)
"""

import math
import random

import rospy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import NavSatFix, NavSatStatus


# Pretend the simulation origin is at this lat/lon (Incheon, KR).
# Choosing realistic coordinates makes the rosbag and RViz overlays
# look credible during the demo video.
ORIGIN_LAT_DEG = 37.4563
ORIGIN_LON_DEG = 126.7052

# Approximate meters per degree at the origin latitude.
METERS_PER_DEG_LAT = 111_320.0
METERS_PER_DEG_LON = 111_320.0 * math.cos(math.radians(ORIGIN_LAT_DEG))


class GpsSimulatorNode:

    def __init__(self):
        self.publish_rate = float(rospy.get_param("~publish_rate", 5.0))
        # Standard deviation of injected GPS noise (meters).
        self.noise_std_m = float(rospy.get_param("~noise_std_m", 0.5))

        self._last_odom = None

        self.fix_pub = rospy.Publisher("/delivery/gps/fix",
                                       NavSatFix, queue_size=10)
        self.odom_sub = rospy.Subscriber("/odom", Odometry,
                                         self.odom_callback, queue_size=1)

        self.timer = rospy.Timer(rospy.Duration(1.0 / self.publish_rate),
                                  self.publish_fix)

        rospy.loginfo("[gps_simulator_node] up. rate=%.1f Hz noise=%.2f m",
                      self.publish_rate, self.noise_std_m)

    def odom_callback(self, msg):
        # Just cache the latest odom. We do not need to publish on every
        # odom message; the timer drives the publication.
        self._last_odom = msg

    def publish_fix(self, _event):
        if self._last_odom is None:
            return

        # Pull the robot position in the local (odom) frame.
        x = self._last_odom.pose.pose.position.x
        y = self._last_odom.pose.pose.position.y

        # Add Gaussian noise to model real-world GPS error.
        x += random.gauss(0.0, self.noise_std_m)
        y += random.gauss(0.0, self.noise_std_m)

        # Convert metric offset to lat/lon delta.
        lat = ORIGIN_LAT_DEG + (y / METERS_PER_DEG_LAT)
        lon = ORIGIN_LON_DEG + (x / METERS_PER_DEG_LON)

        fix = NavSatFix()
        fix.header.stamp = rospy.Time.now()
        fix.header.frame_id = "gps_link"
        fix.status.status = NavSatStatus.STATUS_FIX
        fix.status.service = NavSatStatus.SERVICE_GPS
        fix.latitude = lat
        fix.longitude = lon
        fix.altitude = 0.0
        # Diagonal covariance with variance = noise_std_m squared.
        var = self.noise_std_m ** 2
        fix.position_covariance = [var, 0, 0,
                                   0, var, 0,
                                   0, 0, var * 4.0]
        fix.position_covariance_type = NavSatFix.COVARIANCE_TYPE_DIAGONAL_KNOWN
        self.fix_pub.publish(fix)


def main():
    rospy.init_node("gps_simulator_node", anonymous=False)
    GpsSimulatorNode()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
