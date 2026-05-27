#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
global_planner_helper_node.py
=============================
Owner: Member 4 (Navigation & Planning).

ROS function #2 for Member 4: a Subscriber + Publisher node that
summarises the global plan into a cheap "path summary" topic.

Why?
    move_base publishes its full plan on /move_base/NavfnROS/plan as a
    nav_msgs/Path with hundreds of poses. The CLI and the remote
    monitoring app only need three numbers - planned length, waypoint
    count, and an "is plan valid" flag - so this node computes them
    once and publishes them on a lean topic.

Topics:
    Subscribes : /move_base/NavfnROS/plan    (nav_msgs/Path)
    Publishes  : /delivery/navigation/plan_summary (std_msgs/String JSON)
"""

import json
import math

import rospy
from nav_msgs.msg import Path
from std_msgs.msg import String


class GlobalPlannerHelperNode:

    def __init__(self):
        self.plan_topic = rospy.get_param("~plan_topic",
                                          "/move_base/NavfnROS/plan")
        self.summary_pub = rospy.Publisher(
            "/delivery/navigation/plan_summary", String, queue_size=2, latch=True)
        self.plan_sub = rospy.Subscriber(
            self.plan_topic, Path, self.plan_callback, queue_size=1)
        rospy.loginfo("[global_planner_helper_node] up. subscribed to %s",
                      self.plan_topic)

    def plan_callback(self, msg):
        poses = msg.poses
        # Sum Euclidean distances between consecutive poses to estimate
        # the total planned path length.
        length = 0.0
        for i in range(1, len(poses)):
            dx = poses[i].pose.position.x - poses[i - 1].pose.position.x
            dy = poses[i].pose.position.y - poses[i - 1].pose.position.y
            length += math.hypot(dx, dy)

        payload = {
            "valid": bool(poses),
            "waypoint_count": len(poses),
            "length_m": round(length, 3),
            "frame_id": msg.header.frame_id,
        }
        self.summary_pub.publish(String(data=json.dumps(payload)))


def main():
    rospy.init_node("global_planner_helper_node", anonymous=False)
    GlobalPlannerHelperNode()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
