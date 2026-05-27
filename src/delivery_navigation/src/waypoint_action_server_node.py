#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
waypoint_action_server_node.py
==============================
Owner: Member 4 (Navigation & Planning).

ROS function #1 for Member 4: an Action server.

This node exposes the DeliveryMission action and delegates the actual
metric path planning + execution to move_base. The CLI tool, the
mission FSM and any teammate can submit a goal here and receive live
feedback (distance remaining, percent complete) while the robot is en
route - which satisfies the project requirement for an action with
long-running feedback.

Action:
    /delivery/navigation/deliver_mission (DeliveryMission)

Parameters:
    ~destinations  (dict)  : map of symbolic name -> [x, y, yaw_rad]
                              loaded from waypoints.yaml.
"""

import math

import actionlib
import rospy
import tf2_ros
from geometry_msgs.msg import PoseStamped, Quaternion
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

from delivery_msgs.msg import (DeliveryMissionAction,
                                DeliveryMissionFeedback,
                                DeliveryMissionResult)


def yaw_to_quaternion(yaw):
    """Convert a yaw angle (rad) to a geometry_msgs/Quaternion."""
    q = Quaternion()
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


class WaypointActionServerNode:

    def __init__(self):
        # Symbolic destinations loaded from the parameter server.
        # Example:  destinations: { library: [2.0, 1.0, 0.0],
        #                           cafe:    [5.0, 0.5, 1.57] }
        self.destinations = rospy.get_param("~destinations", {})

        # Robot frame used to compute distance remaining.
        self.robot_frame = rospy.get_param("~robot_frame", "base_link")
        self.global_frame = rospy.get_param("~global_frame", "map")

        # tf2 buffer for distance estimation feedback.
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)

        # Action client to forward goals to move_base.
        self.move_base_client = actionlib.SimpleActionClient(
            "move_base", MoveBaseAction)
        rospy.loginfo("[waypoint_action_server_node] waiting for move_base...")
        ok = self.move_base_client.wait_for_server(rospy.Duration(15.0))
        if not ok:
            rospy.logwarn("[waypoint_action_server_node] move_base not "
                          "available - the action will still accept goals but "
                          "report failure until move_base comes up.")

        # Our own action server.
        self.action_server = actionlib.SimpleActionServer(
            "/delivery/navigation/deliver_mission",
            DeliveryMissionAction,
            execute_cb=self.execute_callback,
            auto_start=False)
        self.action_server.start()

        rospy.loginfo("[waypoint_action_server_node] up. %d destinations loaded.",
                      len(self.destinations))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _resolve_goal(self, goal):
        """
        Decide the metric goal pose. If the goal includes an explicit
        target pose, use it. Otherwise look up the symbolic destination
        in our parameter table.
        """
        # If the goal has any non-zero coordinate, treat it as explicit.
        target = goal.target
        has_explicit = (target.pose.position.x != 0.0
                        or target.pose.position.y != 0.0)
        if has_explicit:
            target.header.frame_id = target.header.frame_id or self.global_frame
            return target

        name = goal.destination_name
        if name not in self.destinations:
            return None
        x, y, yaw = self.destinations[name]
        ps = PoseStamped()
        ps.header.frame_id = self.global_frame
        ps.header.stamp = rospy.Time.now()
        ps.pose.position.x = float(x)
        ps.pose.position.y = float(y)
        ps.pose.orientation = yaw_to_quaternion(float(yaw))
        return ps

    def _robot_xy(self):
        """Return current robot (x, y) in the global frame, or None."""
        try:
            tf = self.tf_buffer.lookup_transform(self.global_frame,
                                                  self.robot_frame,
                                                  rospy.Time(0),
                                                  rospy.Duration(0.5))
            return tf.transform.translation.x, tf.transform.translation.y
        except (tf2_ros.LookupException,
                tf2_ros.ExtrapolationException,
                tf2_ros.ConnectivityException):
            return None

    @staticmethod
    def _xy_distance(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    # ------------------------------------------------------------------
    # Action callback
    # ------------------------------------------------------------------
    def execute_callback(self, goal):
        rospy.loginfo("[waypoint_action_server_node] new goal: name=%s",
                      goal.destination_name)

        target = self._resolve_goal(goal)
        if target is None:
            result = DeliveryMissionResult(success=False,
                                            total_distance_m=0.0,
                                            final_state="FAILED")
            self.action_server.set_aborted(
                result, "unknown destination: %s" % goal.destination_name)
            return

        # Forward to move_base.
        mb_goal = MoveBaseGoal()
        mb_goal.target_pose = target
        self.move_base_client.send_goal(mb_goal)

        start_xy = self._robot_xy()
        target_xy = (target.pose.position.x, target.pose.position.y)
        total_distance = (self._xy_distance(start_xy, target_xy)
                          if start_xy else 0.0)

        # Poll the move_base client and publish feedback at ~2 Hz.
        rate = rospy.Rate(2.0)
        while not rospy.is_shutdown():
            # Allow the client to preempt this goal.
            if self.action_server.is_preempt_requested():
                rospy.logwarn("[waypoint_action_server_node] goal preempted")
                self.move_base_client.cancel_goal()
                result = DeliveryMissionResult(success=False,
                                                total_distance_m=total_distance,
                                                final_state="ABORTED")
                self.action_server.set_preempted(result, "preempted by client")
                return

            state = self.move_base_client.get_state()
            # actionlib_msgs/GoalStatus: 3 = SUCCEEDED.
            if state == 3:
                result = DeliveryMissionResult(success=True,
                                                total_distance_m=total_distance,
                                                final_state="DELIVERED")
                self.action_server.set_succeeded(result, "reached destination")
                return
            # 4 = ABORTED, 5 = REJECTED, 9 = LOST.
            if state in (4, 5, 9):
                result = DeliveryMissionResult(success=False,
                                                total_distance_m=total_distance,
                                                final_state="FAILED")
                self.action_server.set_aborted(result,
                                                "move_base failed (state=%d)" % state)
                return

            # Compute and publish feedback.
            now_xy = self._robot_xy()
            if now_xy is not None and total_distance > 0.0:
                remaining = self._xy_distance(now_xy, target_xy)
                percent = max(0.0,
                              min(100.0,
                                  100.0 * (1.0 - remaining / total_distance)))
            else:
                remaining = 0.0
                percent = 0.0

            fb = DeliveryMissionFeedback()
            fb.distance_remaining_m = float(remaining)
            fb.percent_complete = float(percent)
            fb.current_state = "NAVIGATING"
            self.action_server.publish_feedback(fb)

            rate.sleep()


def main():
    rospy.init_node("waypoint_action_server_node", anonymous=False)
    WaypointActionServerNode()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
