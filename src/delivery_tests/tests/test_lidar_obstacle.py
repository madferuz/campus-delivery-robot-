"""
test_lidar_obstacle.py
======================
Integration test for Member 2's lidar_obstacle_node. Publishes a
synthetic /scan and verifies the node correctly reports the closest
forward obstacle.

Scenarios:
    1. With a fake scan where the closest forward range is 0.4 m, the
       node publishes obstacle.distance ≈ 0.4 m.
    2. With every range = inf, the node publishes distance = -1 and
       confidence = 0.0.
"""

import math
import time

import pytest

pytestmark = pytest.mark.needs_ros


@pytest.fixture(scope="module")
def ros_node():
    import rospy
    rospy.init_node("test_lidar_obstacle",
                    anonymous=True, disable_signals=True)
    return rospy


def _build_scan(ranges, angle_min=-math.pi, angle_max=math.pi):
    from sensor_msgs.msg import LaserScan
    scan = LaserScan()
    scan.header.frame_id = "base_scan"
    scan.angle_min = angle_min
    scan.angle_max = angle_max
    scan.angle_increment = (angle_max - angle_min) / len(ranges)
    scan.range_min = 0.05
    scan.range_max = 12.0
    scan.ranges = ranges
    return scan


def _await_obstacle(timeout=3.0):
    import rospy
    from delivery_msgs.msg import ObstacleInfo
    last = {"msg": None}

    def _cb(msg):
        last["msg"] = msg

    sub = rospy.Subscriber("/delivery/perception/lidar/obstacle",
                            ObstacleInfo, _cb)
    deadline = time.time() + timeout
    while last["msg"] is None and time.time() < deadline:
        time.sleep(0.05)
    sub.unregister()
    return last["msg"]


def test_finds_closest_forward(ros_node):
    import rospy
    from sensor_msgs.msg import LaserScan

    pub = rospy.Publisher("/scan", LaserScan, queue_size=1, latch=True)
    time.sleep(1.0)  # let the latched publisher register

    # 360 rays. Index ~180 corresponds to "directly forward" given the
    # angle_min = -pi / angle_max = pi convention. Set it to 0.4 m.
    ranges = [10.0] * 360
    ranges[180] = 0.4
    pub.publish(_build_scan(ranges))

    msg = _await_obstacle()
    assert msg is not None, "no ObstacleInfo received"
    assert msg.distance == pytest.approx(0.4, abs=0.05)
    assert msg.confidence > 0.5


def test_handles_all_inf(ros_node):
    import rospy
    from sensor_msgs.msg import LaserScan

    pub = rospy.Publisher("/scan", LaserScan, queue_size=1, latch=True)
    time.sleep(1.0)

    ranges = [float("inf")] * 360
    pub.publish(_build_scan(ranges))

    msg = _await_obstacle()
    assert msg is not None
    assert msg.distance == -1.0
    assert msg.confidence == 0.0
