#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
delivery_box_service_node.py
============================
Owner: Member 6 (Mission Control & Delivery).

ROS function #1 for Member 6: a Service server that controls the
robot's delivery box lid.

Because we are running in simulation we cannot actually toggle a servo,
so we model the lid in software:
  - The lid takes `~actuation_time_s` seconds to move.
  - During that time, additional service calls return success=False
    with an explanatory message.
  - The current state is published on a latched topic so subscribers
    always see the latest value.

Services:
    Advertises : /delivery/box/open_delivery_box   (OpenDeliveryBox)

Topics:
    Publishes  : /delivery/box/state               (std_msgs/Bool, latched)
"""

import time

import rospy
from std_msgs.msg import Bool

from delivery_msgs.srv import OpenDeliveryBox, OpenDeliveryBoxResponse


class DeliveryBoxServiceNode:

    def __init__(self):
        # Simulated time for the lid actuator to complete one move.
        self.actuation_time_s = float(rospy.get_param("~actuation_time_s", 1.5))

        # Lid is closed at boot.
        self._is_open = False
        self._moving = False

        # Latched publisher so late subscribers immediately know the state.
        self.state_pub = rospy.Publisher("/delivery/box/state", Bool,
                                          queue_size=1, latch=True)
        self.state_pub.publish(Bool(data=self._is_open))

        self.service = rospy.Service("/delivery/box/open_delivery_box",
                                      OpenDeliveryBox,
                                      self.handle_request)

        rospy.loginfo("[delivery_box_service_node] up. actuation=%.1f s",
                      self.actuation_time_s)

    def handle_request(self, req):
        if self._moving:
            return OpenDeliveryBoxResponse(success=False,
                                            message="actuator already moving")

        if req.open == self._is_open:
            return OpenDeliveryBoxResponse(success=True,
                                            message="already in requested state")

        self._moving = True
        rospy.loginfo("[delivery_box_service_node] %s box ...",
                      "opening" if req.open else "closing")
        # Simulate actuation. rospy.sleep cooperates with shutdowns.
        rospy.sleep(self.actuation_time_s)

        self._is_open = bool(req.open)
        self._moving = False
        self.state_pub.publish(Bool(data=self._is_open))

        msg = "box opened" if self._is_open else "box closed"
        rospy.loginfo("[delivery_box_service_node] %s", msg)
        return OpenDeliveryBoxResponse(success=True, message=msg)


def main():
    rospy.init_node("delivery_box_service_node", anonymous=False)
    DeliveryBoxServiceNode()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
