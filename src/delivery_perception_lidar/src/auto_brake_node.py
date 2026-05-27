#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_brake_node.py
==================
Owner: Member 2 (LiDAR perception & safety).

ROS function #2 for Member 2: a Service server combined with a
Subscriber/Publisher loop that implements automatic emergency braking.

Behavior:
  - Subscribes to the summarised LiDAR obstacle topic.
  - If the closest forward obstacle is below `brake_distance` meters,
    publishes a zero Twist on /cmd_vel and engages the emergency stop.
  - Also exposes an EmergencyStop service so the CLI or a teammate's
    node can engage/release the brake manually.

This satisfies the "Service request/reply" ROS feature requirement.

Topics:
    Subscribes : /delivery/perception/lidar/obstacle  (ObstacleInfo)
    Publishes  : /cmd_vel                             (geometry_msgs/Twist)
                 /delivery/safety/brake_engaged       (std_msgs/Bool)

Services:
    Advertises : /delivery/safety/emergency_stop      (EmergencyStop)
"""

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool

from delivery_msgs.msg import ObstacleInfo
from delivery_msgs.srv import EmergencyStop, EmergencyStopResponse


class AutoBrakeNode:
    """Stops the robot when an obstacle is too close."""

    def __init__(self):
        # Distance threshold under which we engage the brake.
        self.brake_distance = float(rospy.get_param("~brake_distance", 0.35))

        # If True the brake stays engaged until a human releases it via
        # the service. If False the brake automatically releases when the
        # obstacle clears.
        self.latch_until_clear = bool(rospy.get_param("~latch_until_clear",
                                                       False))

        self._brake_engaged = False
        self._brake_reason = ""

        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=1)
        self.status_pub = rospy.Publisher(
            "/delivery/safety/brake_engaged", Bool, queue_size=1, latch=True)

        self.lidar_sub = rospy.Subscriber(
            "/delivery/perception/lidar/obstacle",
            ObstacleInfo, self.lidar_callback, queue_size=1)

        # Service for manual / external brake control.
        self.stop_srv = rospy.Service(
            "/delivery/safety/emergency_stop",
            EmergencyStop, self.handle_emergency_stop)

        rospy.loginfo("[auto_brake_node] up. brake_distance=%.2f m",
                      self.brake_distance)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _engage(self, reason):
        """Publish a zero Twist and set the brake-engaged flag."""
        if not self._brake_engaged:
            rospy.logwarn("[auto_brake_node] BRAKE engaged: %s", reason)
        self._brake_engaged = True
        self._brake_reason = reason
        # Publishing a zero Twist on /cmd_vel is the cleanest way to
        # halt the TurtleBot3 base in simulation.
        self.cmd_pub.publish(Twist())
        self.status_pub.publish(Bool(data=True))

    def _release(self, reason):
        if self._brake_engaged:
            rospy.loginfo("[auto_brake_node] brake released: %s", reason)
        self._brake_engaged = False
        self._brake_reason = ""
        self.status_pub.publish(Bool(data=False))

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def lidar_callback(self, msg):
        # Valid distances are positive. -1 means "no reading".
        too_close = (msg.distance > 0.0) and (msg.distance < self.brake_distance)

        if too_close:
            self._engage("LiDAR obstacle at %.2f m" % msg.distance)
            return

        # Obstacle has cleared. Whether we auto-release depends on the
        # latch parameter.
        if self._brake_engaged and not self.latch_until_clear:
            self._release("forward arc clear")

    def handle_emergency_stop(self, req):
        """Service callback used by the CLI / mission node."""
        if req.engage:
            self._engage("service request: %s" % req.reason)
        else:
            self._release("service release: %s" % req.reason)
        return EmergencyStopResponse(success=True)


def main():
    rospy.init_node("auto_brake_node", anonymous=False)
    AutoBrakeNode()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
