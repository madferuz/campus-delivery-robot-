#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vision_detector_node.py
=======================
Owner: Member 1 (Vision Perception)

ROS function #2 for Member 1: a Subscriber/Publisher node that runs
OpenCV-based detection.

The node subscribes to the canonical processed camera stream published
by camera_publisher_node and runs two detectors:

  1. Pedestrian detector       - HOG + SVM person detector (cv2).
  2. Generic obstacle detector - simple low-light / large-blob detector
                                 used as a fallback when HOG fails.

When something is detected the node publishes an ObstacleInfo on
/delivery/perception/vision/obstacles so that the mission node can
react (slow down, brake, replan, ...).

Topics:
    Subscribes : /delivery/camera/image            (sensor_msgs/Image)
    Publishes  : /delivery/perception/vision/obstacles
                                                   (delivery_msgs/ObstacleInfo)
                 /delivery/perception/vision/annotated
                                                   (sensor_msgs/Image)
"""

import math

import cv2
import numpy as np
import rospy
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image

from delivery_msgs.msg import ObstacleInfo


class VisionDetectorNode:
    """OpenCV-based pedestrian and obstacle detector."""

    # Camera horizontal field of view assumption for the TB3 model.
    # Used to convert pixel column -> bearing angle.
    CAMERA_HFOV_RAD = math.radians(60.0)

    # Rough mapping from detected bounding box height to distance.
    # height_px = K / distance_m.  K is calibrated empirically; the value
    # below is a reasonable default for the TurtleBot3 sim camera and is
    # good enough for the behavior logic that consumes this distance.
    DISTANCE_K = 320.0

    def __init__(self):
        self.image_topic = rospy.get_param("~image_topic",
                                           "/delivery/camera/image")
        self.min_confidence = float(rospy.get_param("~min_confidence", 0.4))

        self.bridge = CvBridge()

        # HOG descriptor pre-trained for people detection - works well
        # enough for the simulated environment.
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        self.obstacle_pub = rospy.Publisher(
            "/delivery/perception/vision/obstacles",
            ObstacleInfo, queue_size=10)

        self.annotated_pub = rospy.Publisher(
            "/delivery/perception/vision/annotated",
            Image, queue_size=2)

        self.image_sub = rospy.Subscriber(
            self.image_topic, Image, self.image_callback,
            queue_size=1, buff_size=2 ** 24)

        rospy.loginfo("[vision_detector_node] up. subscribed to %s",
                      self.image_topic)

    # ------------------------------------------------------------------
    # Detection helpers
    # ------------------------------------------------------------------
    def detect_pedestrians(self, frame):
        """Return list of (x, y, w, h, confidence) for detected people."""
        # detectMultiScale returns boxes and per-box weights (confidence).
        boxes, weights = self.hog.detectMultiScale(
            frame, winStride=(8, 8), padding=(8, 8), scale=1.05)
        results = []
        for box, weight in zip(boxes, weights):
            x, y, w, h = box
            # Normalise the SVM score to a rough confidence in [0, 1].
            conf = float(min(1.0, max(0.0, weight / 2.0)))
            if conf >= self.min_confidence:
                results.append((x, y, w, h, conf))
        return results

    def detect_obstacles(self, frame):
        """
        Detect generic obstacles using simple thresholding + contour
        analysis. This is intentionally lightweight: it acts as a
        fallback for static obstacles that HOG won't catch.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Adaptive threshold isolates dark regions that may be obstacles.
        thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
            blockSize=21, C=10)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        results = []
        h_img, w_img = frame.shape[:2]
        min_area = (w_img * h_img) * 0.02  # ignore tiny noise blobs
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            # Heuristic: obstacles tend to sit in the lower half.
            if (y + h) < h_img * 0.4:
                continue
            results.append((x, y, w, h, 0.5))
        return results

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------
    def box_to_bearing(self, box, image_width):
        """Convert a bounding box centre to a bearing in radians."""
        x, _, w, _ = box[:4]
        cx = x + w / 2.0
        # Map pixel column [0, image_width] to [-HFOV/2, +HFOV/2].
        # Positive bearing means the obstacle is to the robot's left.
        normalized = (cx / float(image_width)) * 2.0 - 1.0  # in [-1, 1]
        return -normalized * (self.CAMERA_HFOV_RAD / 2.0)

    def box_to_distance(self, box):
        """Estimate distance to obstacle from bounding box height."""
        _, _, _, h = box[:4]
        if h <= 0:
            return float("inf")
        return self.DISTANCE_K / float(h)

    # ------------------------------------------------------------------
    # ROS callback
    # ------------------------------------------------------------------
    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(5.0,
                                   "[vision_detector_node] cv_bridge: %s",
                                   str(exc))
            return

        img_h, img_w = frame.shape[:2]
        annotated = frame.copy()

        # --- Run pedestrian detection (priority obstacle type) ---
        for (x, y, w, h, conf) in self.detect_pedestrians(frame):
            distance = self.box_to_distance((x, y, w, h))
            bearing = self.box_to_bearing((x, y, w, h), img_w)
            self._publish_obstacle("pedestrian", distance, bearing, conf,
                                   msg.header.stamp)
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(annotated, "person %.2f" % conf, (x, max(0, y - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # --- Run generic obstacle detection ---
        for (x, y, w, h, conf) in self.detect_obstacles(frame):
            distance = self.box_to_distance((x, y, w, h))
            bearing = self.box_to_bearing((x, y, w, h), img_w)
            self._publish_obstacle("object", distance, bearing, conf,
                                   msg.header.stamp)
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 200, 255), 2)

        # Publish the annotated debug image (visible in RViz).
        try:
            out_msg = self.bridge.cv2_to_imgmsg(annotated, encoding="bgr8")
            out_msg.header = msg.header
            self.annotated_pub.publish(out_msg)
        except CvBridgeError:
            pass

    def _publish_obstacle(self, obstacle_type, distance, bearing,
                          confidence, stamp):
        info = ObstacleInfo()
        info.header.stamp = stamp
        info.header.frame_id = "camera_rgb_optical_frame"
        info.obstacle_type = obstacle_type
        info.distance = float(distance)
        info.bearing = float(bearing)
        info.confidence = float(confidence)
        self.obstacle_pub.publish(info)


def main():
    rospy.init_node("vision_detector_node", anonymous=False)
    VisionDetectorNode()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
