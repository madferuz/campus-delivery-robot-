#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
map_tf_broadcaster_node.py
==========================
Owner: Member 3 (Localization & TF).

ROS function #2 for Member 3: a tf2 broadcaster + Subscriber that keeps
the map -> odom transform consistent.

Why this node?
    When we are not running the full AMCL stack (e.g. during the rosbag
    replay tests, or while bringing up only part of the system) the
    /map -> /odom transform is missing, which breaks every consumer
    that asks the tf tree for the robot's pose in /map.
    This node bridges the gap by publishing a configurable static
    transform and updating it whenever the user clicks
    "2D Pose Estimate" in RViz (which sends an /initialpose message).

Topics:
    Subscribes : /initialpose      (geometry_msgs/PoseWithCovarianceStamped)

TF:
    Broadcasts : /map -> /odom
"""

import rospy
import tf2_ros
from geometry_msgs.msg import TransformStamped, PoseWithCovarianceStamped


class MapTfBroadcasterNode:

    def __init__(self):
        self.publish_rate = float(rospy.get_param("~publish_rate", 20.0))

        # Initial offset between /map and /odom. Defaults to zero, i.e.
        # the two frames coincide which is the standard simulation case.
        self._tx = float(rospy.get_param("~initial_x", 0.0))
        self._ty = float(rospy.get_param("~initial_y", 0.0))
        self._tz = float(rospy.get_param("~initial_z", 0.0))
        self._qx = float(rospy.get_param("~initial_qx", 0.0))
        self._qy = float(rospy.get_param("~initial_qy", 0.0))
        self._qz = float(rospy.get_param("~initial_qz", 0.0))
        self._qw = float(rospy.get_param("~initial_qw", 1.0))

        self.broadcaster = tf2_ros.TransformBroadcaster()

        # RViz "2D Pose Estimate" publishes on /initialpose. We use it
        # to let the user manually reseed our transform during the demo.
        self.pose_sub = rospy.Subscriber("/initialpose",
                                          PoseWithCovarianceStamped,
                                          self.initial_pose_callback)

        self.timer = rospy.Timer(rospy.Duration(1.0 / self.publish_rate),
                                  self.publish_tf)

        rospy.loginfo("[map_tf_broadcaster_node] up. rate=%.1f Hz",
                      self.publish_rate)

    def initial_pose_callback(self, msg):
        """Update the broadcast transform from an RViz pose estimate."""
        rospy.loginfo("[map_tf_broadcaster_node] received initial pose")
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        self._tx, self._ty, self._tz = p.x, p.y, p.z
        self._qx, self._qy, self._qz, self._qw = q.x, q.y, q.z, q.w

    def publish_tf(self, _event):
        tf_msg = TransformStamped()
        tf_msg.header.stamp = rospy.Time.now()
        tf_msg.header.frame_id = "map"
        tf_msg.child_frame_id = "odom"
        tf_msg.transform.translation.x = self._tx
        tf_msg.transform.translation.y = self._ty
        tf_msg.transform.translation.z = self._tz
        tf_msg.transform.rotation.x = self._qx
        tf_msg.transform.rotation.y = self._qy
        tf_msg.transform.rotation.z = self._qz
        tf_msg.transform.rotation.w = self._qw
        self.broadcaster.sendTransform(tf_msg)


def main():
    rospy.init_node("map_tf_broadcaster_node", anonymous=False)
    MapTfBroadcasterNode()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
