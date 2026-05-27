#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
remote_telemetry_node.py
========================
Owner: Member 5 (Voice & Remote interface).

ROS function #2 for Member 5: a multi-Subscriber + single Publisher
node that aggregates information from the rest of the system into a
compact JSON telemetry string. The "Remote Monitoring App" mentioned
in the project brief consumes this single topic instead of subscribing
to half a dozen heterogeneous topics.

Topics:
    Subscribes : /delivery/gps/fix                    (NavSatFix)
                 /delivery/status                     (RobotStatus)
                 /delivery/safety/brake_engaged       (std_msgs/Bool)
                 /delivery/navigation/plan_summary    (std_msgs/String JSON)

    Publishes  : /delivery/remote/telemetry           (std_msgs/String JSON)
"""

import json

import rospy
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Bool, String

from delivery_msgs.msg import RobotStatus


class RemoteTelemetryNode:

    def __init__(self):
        self.publish_rate = float(rospy.get_param("~publish_rate", 2.0))

        # Internal caches updated by subscribers and published by timer.
        self._gps = None
        self._status = None
        self._brake = False
        self._plan_summary = None

        rospy.Subscriber("/delivery/gps/fix", NavSatFix, self._on_gps,
                          queue_size=1)
        rospy.Subscriber("/delivery/status", RobotStatus, self._on_status,
                          queue_size=1)
        rospy.Subscriber("/delivery/safety/brake_engaged", Bool, self._on_brake,
                          queue_size=1)
        rospy.Subscriber("/delivery/navigation/plan_summary", String,
                          self._on_plan_summary, queue_size=1)

        self.telemetry_pub = rospy.Publisher("/delivery/remote/telemetry",
                                              String, queue_size=2)

        self.timer = rospy.Timer(rospy.Duration(1.0 / self.publish_rate),
                                  self._publish)

        rospy.loginfo("[remote_telemetry_node] up. rate=%.1f Hz",
                      self.publish_rate)

    # ------------------------------------------------------------------
    # Subscriber callbacks - just cache the latest value.
    # ------------------------------------------------------------------
    def _on_gps(self, msg):
        self._gps = {"lat": msg.latitude, "lon": msg.longitude,
                     "alt": msg.altitude}

    def _on_status(self, msg):
        self._status = {
            "state": msg.state,
            "battery_percent": round(msg.battery_percent, 1),
            "delivery_box_open": msg.delivery_box_open,
            "pose_xy": [msg.pose.position.x, msg.pose.position.y],
            "info": msg.info,
        }

    def _on_brake(self, msg):
        self._brake = bool(msg.data)

    def _on_plan_summary(self, msg):
        try:
            self._plan_summary = json.loads(msg.data)
        except ValueError:
            self._plan_summary = None

    # ------------------------------------------------------------------
    # Periodic publisher.
    # ------------------------------------------------------------------
    def _publish(self, _event):
        payload = {
            "stamp": rospy.Time.now().to_sec(),
            "gps": self._gps,
            "status": self._status,
            "brake_engaged": self._brake,
            "plan_summary": self._plan_summary,
        }
        self.telemetry_pub.publish(String(data=json.dumps(payload)))


def main():
    rospy.init_node("remote_telemetry_node", anonymous=False)
    RemoteTelemetryNode()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
