#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mission_fsm_node.py
===================
Owner: Member 6 (Mission Control & Delivery).

ROS function #2 for Member 6: a Subscriber + Publisher + ActionClient
node that implements the high-level state machine described in the
project flowchart:

    IDLE -> RECEIVING_COMMAND -> NAVIGATING ->
        (AVOIDING | STOPPED_FOR_PEDESTRIAN)* ->
        AT_DESTINATION -> RETURNING -> IDLE

This is the "brain" of the robot. It listens for voice commands, talks
to the navigation action, opens the delivery box on arrival, and then
sends the robot home.

Topics:
    Subscribes : /delivery/voice/commands             (VoiceCommand)
                 /delivery/perception/vision/obstacles(ObstacleInfo)
                 /odom                                (nav_msgs/Odometry)
    Publishes  : /delivery/status                     (RobotStatus)

Action client:
    /delivery/navigation/deliver_mission              (DeliveryMission)

Services used:
    /delivery/box/open_delivery_box                   (OpenDeliveryBox)
"""

import actionlib
import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry

from delivery_msgs.msg import (DeliveryMissionAction, DeliveryMissionGoal,
                                ObstacleInfo, RobotStatus, VoiceCommand)
from delivery_msgs.srv import OpenDeliveryBox


# Battery model: drain `BATTERY_DRAIN_PER_S` percent per second of run
# time. Purely cosmetic, used by the remote monitoring screen.
BATTERY_DRAIN_PER_S = 0.05


class MissionFsmNode:

    # ------------------------------------------------------------------
    # State strings (mirrors RobotStatus.state).
    # ------------------------------------------------------------------
    IDLE = "IDLE"
    RECEIVING = "RECEIVING_COMMAND"
    NAVIGATING = "NAVIGATING"
    STOPPED = "STOPPED_FOR_PEDESTRIAN"
    AT_DEST = "AT_DESTINATION"
    RETURNING = "RETURNING"
    ERROR = "ERROR"

    def __init__(self):
        self.home_destination = rospy.get_param("~home_destination", "home")

        self.state = self.IDLE
        self.info_msg = ""
        self.battery_percent = 100.0
        self._latest_pose = None
        self._delivery_box_open = False
        self._start_time = rospy.Time.now()

        # Action client for navigation.
        self.nav_client = actionlib.SimpleActionClient(
            "/delivery/navigation/deliver_mission", DeliveryMissionAction)
        rospy.loginfo("[mission_fsm_node] waiting for navigation action...")
        self.nav_client.wait_for_server(rospy.Duration(15.0))

        # Service proxy to the delivery box.
        rospy.wait_for_service("/delivery/box/open_delivery_box",
                                timeout=15.0)
        self.box_srv = rospy.ServiceProxy(
            "/delivery/box/open_delivery_box", OpenDeliveryBox)

        # Publishers / subscribers.
        self.status_pub = rospy.Publisher("/delivery/status", RobotStatus,
                                           queue_size=2)
        rospy.Subscriber("/delivery/voice/commands", VoiceCommand,
                          self._on_voice, queue_size=10)
        rospy.Subscriber("/delivery/perception/vision/obstacles",
                          ObstacleInfo, self._on_obstacle, queue_size=10)
        rospy.Subscriber("/odom", Odometry, self._on_odom, queue_size=1)

        # Status publish timer.
        rospy.Timer(rospy.Duration(0.5), self._publish_status)

        rospy.loginfo("[mission_fsm_node] up. state=%s", self.state)

    # ------------------------------------------------------------------
    # Subscriber callbacks
    # ------------------------------------------------------------------
    def _on_voice(self, msg):
        if msg.confidence < 0.5:
            return
        rospy.loginfo("[mission_fsm_node] voice cmd %s target=%s",
                      msg.command, msg.target)

        if msg.command == "deliver":
            if self.state != self.IDLE:
                rospy.logwarn("[mission_fsm_node] busy, ignoring deliver "
                              "command (state=%s)", self.state)
                return
            self._set_state(self.RECEIVING, "received delivery request")
            self._run_delivery(msg.target or "library")

        elif msg.command == "stop":
            # Cancel any active navigation goal.
            self.nav_client.cancel_all_goals()
            self._set_state(self.IDLE, "stopped by voice command")

        elif msg.command == "return_home":
            if self.state == self.IDLE:
                self._run_return_home()

        elif msg.command == "open_box":
            self._call_box(True)

    def _on_obstacle(self, msg):
        # We only react to pedestrians here - generic obstacles are
        # already handled by the auto_brake node. Pedestrians need a
        # softer behavior (wait, then continue) rather than a hard stop.
        if msg.obstacle_type != "pedestrian":
            return
        if msg.distance > 0.0 and msg.distance < 1.5 \
                and self.state == self.NAVIGATING:
            self._set_state(self.STOPPED, "pedestrian at %.2f m" % msg.distance)
        elif self.state == self.STOPPED and msg.distance > 2.0:
            self._set_state(self.NAVIGATING, "pedestrian cleared")

    def _on_odom(self, msg):
        self._latest_pose = msg.pose.pose

    # ------------------------------------------------------------------
    # Mission helpers
    # ------------------------------------------------------------------
    def _run_delivery(self, destination):
        self._set_state(self.NAVIGATING, "navigating to %s" % destination)
        goal = DeliveryMissionGoal()
        goal.destination_name = destination
        goal.target = PoseStamped()  # let the action server fill from name
        self.nav_client.send_goal_and_wait(goal)
        result = self.nav_client.get_result()

        if result and result.success:
            self._set_state(self.AT_DEST, "arrived at %s" % destination)
            self._call_box(True)
            rospy.sleep(2.0)   # short window for the user to retrieve item
            self._call_box(False)
            self._run_return_home()
        else:
            self._set_state(self.ERROR, "navigation failed")

    def _run_return_home(self):
        self._set_state(self.RETURNING, "returning home")
        goal = DeliveryMissionGoal()
        goal.destination_name = self.home_destination
        goal.target = PoseStamped()
        self.nav_client.send_goal_and_wait(goal)
        result = self.nav_client.get_result()
        if result and result.success:
            self._set_state(self.IDLE, "home")
        else:
            self._set_state(self.ERROR, "could not return home")

    def _call_box(self, open_lid):
        try:
            resp = self.box_srv(open=open_lid)
            self._delivery_box_open = bool(open_lid) if resp.success \
                else self._delivery_box_open
        except rospy.ServiceException as exc:
            rospy.logwarn("[mission_fsm_node] box service failed: %s", exc)

    # ------------------------------------------------------------------
    # State + status helpers
    # ------------------------------------------------------------------
    def _set_state(self, state, info):
        rospy.loginfo("[mission_fsm_node] %s -> %s : %s",
                      self.state, state, info)
        self.state = state
        self.info_msg = info

    def _publish_status(self, _event):
        # Simple battery model.
        elapsed = (rospy.Time.now() - self._start_time).to_sec()
        self.battery_percent = max(0.0,
                                    100.0 - elapsed * BATTERY_DRAIN_PER_S)

        msg = RobotStatus()
        msg.header.stamp = rospy.Time.now()
        msg.state = self.state
        msg.battery_percent = float(self.battery_percent)
        if self._latest_pose:
            msg.pose = self._latest_pose
        msg.delivery_box_open = self._delivery_box_open
        msg.info = self.info_msg
        self.status_pub.publish(msg)


def main():
    rospy.init_node("mission_fsm_node", anonymous=False)
    MissionFsmNode()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
