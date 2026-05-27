#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lidar_obstacle_node.py
======================
Owner: Member 2 (LiDAR perception & safety).

ROS function #1 for Member 2: a Subscriber + Publisher node that
distills the raw /scan stream into a single "closest forward obstacle"
message that downstream behaviors can consume cheaply.

Why summarise?
    The raw LaserScan has hundreds of ranges per frame. Most consumers
    (auto brake, mission FSM, CLI status) only need one number: how
    close is the nearest thing in the forward arc. Doing this
    summarisation once in a dedicated node keeps the rest of the system
    simple and avoids each consumer re-implementing the same logic.

Topics:
    Subscribes : /scan                                  (sensor_msgs/LaserScan)
    Publishes  : /delivery/perception/lidar/obstacle    (delivery_msgs/ObstacleInfo)
"""

import math

import rospy
from sensor_msgs.msg import LaserScan

from delivery_msgs.msg import ObstacleInfo


class LidarObstacleNode:
    """Find the closest point in a forward arc and publish ObstacleInfo."""

    def __init__(self):
        # Half-width of the arc (radians) used to look "forward".
        # 0.52 rad ≈ 30 degrees on each side of the heading.
        self.forward_half_angle = float(
            rospy.get_param("~forward_half_angle", 0.52))

        # Range readings below this are treated as sensor noise / errors.
        self.min_valid_range = float(rospy.get_param("~min_valid_range", 0.05))

        self.scan_sub = rospy.Subscriber("/scan", LaserScan,
                                         self.scan_callback, queue_size=1)

        self.obstacle_pub = rospy.Publisher(
            "/delivery/perception/lidar/obstacle",
            ObstacleInfo, queue_size=10)

        rospy.loginfo("[lidar_obstacle_node] up. forward_half_angle=%.2f rad",
                      self.forward_half_angle)

    def scan_callback(self, scan):
        # Iterate every range in the scan and keep the closest one that
        # falls inside the forward arc. We could do this with numpy for
        # extra speed, but the explicit loop reads more clearly for the
        # report and the scan is small.
        min_range = float("inf")
        min_bearing = 0.0
        angle = scan.angle_min

        for r in scan.ranges:
            # angle_min/max wrap differently depending on the driver, so
            # compute on the fly rather than precomputing once.
            in_forward_arc = (
                angle >= -self.forward_half_angle
                and angle <= self.forward_half_angle
            )
            if (in_forward_arc
                    and not math.isinf(r)
                    and not math.isnan(r)
                    and r >= self.min_valid_range
                    and r < min_range):
                min_range = r
                min_bearing = angle
            angle += scan.angle_increment

        info = ObstacleInfo()
        info.header.stamp = scan.header.stamp
        info.header.frame_id = scan.header.frame_id
        info.obstacle_type = "object" if not math.isinf(min_range) else "unknown"
        info.distance = float(min_range) if not math.isinf(min_range) else -1.0
        info.bearing = float(min_bearing)
        info.confidence = 1.0 if not math.isinf(min_range) else 0.0
        self.obstacle_pub.publish(info)


def main():
    rospy.init_node("lidar_obstacle_node", anonymous=False)
    LidarObstacleNode()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
