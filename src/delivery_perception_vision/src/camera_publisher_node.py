#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
camera_publisher_node.py
========================
Owner: Member 1 (Vision Perception)

ROS function #1 for Member 1: a Publisher node.

This node bridges the raw Gazebo camera output (sensor_msgs/Image on the
TurtleBot3 camera topic) into a canonical topic that the rest of the
system listens to. It also applies a light preprocessing pass
(resize + optional grayscale) and republishes a Compressed image stream
that the remote monitoring app can consume cheaply.

Parameters (ROS Parameter Server):
    ~input_topic   (str) : Gazebo camera topic to subscribe to.
                           Default: "/camera/rgb/image_raw".
    ~output_topic  (str) : Topic to publish processed frames on.
                           Default: "/delivery/camera/image".
    ~target_width  (int) : Width to resize incoming frames to. Default 320.
    ~target_height (int) : Height to resize incoming frames to. Default 240.
    ~publish_rate  (float): Max publish rate in Hz. Default 10.0.

Topics:
    Subscribes : <input_topic>  (sensor_msgs/Image)
    Publishes  : <output_topic> (sensor_msgs/Image)
                 <output_topic>/compressed (sensor_msgs/CompressedImage)
"""

import rospy
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image, CompressedImage


class CameraPublisherNode:
    """Republishes Gazebo camera frames at a controlled rate and size."""

    def __init__(self):
        # Read parameters with sensible defaults so the node works even
        # if no parameter file is loaded.
        self.input_topic = rospy.get_param("~input_topic",
                                           "/camera/rgb/image_raw")
        self.output_topic = rospy.get_param("~output_topic",
                                            "/delivery/camera/image")
        self.target_width = int(rospy.get_param("~target_width", 320))
        self.target_height = int(rospy.get_param("~target_height", 240))
        self.publish_rate = float(rospy.get_param("~publish_rate", 10.0))

        # cv_bridge converts between ROS Image messages and OpenCV ndarrays.
        self.bridge = CvBridge()

        # Track last publish time to throttle the output stream.
        self._last_publish_time = rospy.Time(0)
        self._min_period = rospy.Duration(1.0 / self.publish_rate)

        # Publishers: raw resized stream and a lightweight compressed stream.
        self.image_pub = rospy.Publisher(self.output_topic, Image, queue_size=2)
        self.compressed_pub = rospy.Publisher(self.output_topic + "/compressed",
                                              CompressedImage, queue_size=2)

        # Subscriber to Gazebo camera. queue_size=1 + buff_size keeps latency low.
        self.image_sub = rospy.Subscriber(self.input_topic, Image,
                                          self.image_callback,
                                          queue_size=1, buff_size=2 ** 24)

        rospy.loginfo("[camera_publisher_node] up. in=%s out=%s size=%dx%d rate=%.1f",
                      self.input_topic, self.output_topic,
                      self.target_width, self.target_height,
                      self.publish_rate)

    def image_callback(self, msg):
        """Resize and republish each incoming Gazebo frame."""
        # Throttle: drop frames that arrive faster than publish_rate.
        now = rospy.Time.now()
        if (now - self._last_publish_time) < self._min_period:
            return
        self._last_publish_time = now

        try:
            # Convert ROS Image to OpenCV BGR matrix.
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(5.0,
                                   "[camera_publisher_node] cv_bridge error: %s",
                                   str(exc))
            return

        # Resize for downstream nodes (saves CPU on detection node).
        resized = cv2.resize(frame, (self.target_width, self.target_height),
                              interpolation=cv2.INTER_AREA)

        # Publish raw (BGR) frame.
        try:
            out_msg = self.bridge.cv2_to_imgmsg(resized, encoding="bgr8")
            out_msg.header = msg.header  # preserve original timestamp / frame
            self.image_pub.publish(out_msg)
        except CvBridgeError as exc:
            rospy.logwarn_throttle(5.0,
                                   "[camera_publisher_node] publish error: %s",
                                   str(exc))

        # Publish JPEG compressed frame for the remote monitoring app.
        ok, encoded = cv2.imencode(".jpg", resized,
                                    [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if ok:
            comp_msg = CompressedImage()
            comp_msg.header = msg.header
            comp_msg.format = "jpeg"
            comp_msg.data = encoded.tobytes()
            self.compressed_pub.publish(comp_msg)


def main():
    rospy.init_node("camera_publisher_node", anonymous=False)
    CameraPublisherNode()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
