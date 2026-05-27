"""
test_delivery_box_service.py
============================
Integration test for Member 6's delivery_box_service_node.

The test brings up the service (via the .test rostest file) and then
verifies the documented behaviour using a Python service client. Run
with:

    rostest delivery_tests test_delivery_box_service.test

or with pytest after sourcing devel/setup.bash:

    pytest --with-ros src/delivery_tests/tests/test_delivery_box_service.py

Scenarios:
    1. The service starts up and the box is initially CLOSED.
    2. open=True closes the request and the state topic latches True.
    3. open=False returns to closed.
    4. Calling open=True twice returns success but message says
       "already in requested state".
"""

import time

import pytest

pytestmark = pytest.mark.needs_ros


@pytest.fixture(scope="module")
def ros_node():
    """Initialise a single rospy node for the whole test module."""
    import rospy
    rospy.init_node("test_delivery_box_service",
                    anonymous=True, disable_signals=True)
    yield rospy
    # rospy nodes cannot easily be re-init'd, so we just let the
    # process exit drop the resources.


@pytest.fixture(scope="module")
def service_proxy(ros_node):
    import rospy
    from delivery_msgs.srv import OpenDeliveryBox
    rospy.wait_for_service("/delivery/box/open_delivery_box", timeout=10.0)
    return rospy.ServiceProxy("/delivery/box/open_delivery_box",
                               OpenDeliveryBox)


def _latest_state(timeout=3.0):
    """Read the latched /delivery/box/state value."""
    import rospy
    from std_msgs.msg import Bool
    box = {"value": None}

    def _cb(msg):
        box["value"] = msg.data

    sub = rospy.Subscriber("/delivery/box/state", Bool, _cb)
    deadline = time.time() + timeout
    while box["value"] is None and time.time() < deadline:
        time.sleep(0.05)
    sub.unregister()
    return box["value"]


def test_box_starts_closed(service_proxy):
    state = _latest_state()
    assert state is False, "delivery box should start closed"


def test_box_opens(service_proxy):
    resp = service_proxy(open=True)
    assert resp.success is True
    assert _latest_state() is True


def test_box_closes(service_proxy):
    resp = service_proxy(open=False)
    assert resp.success is True
    assert _latest_state() is False


def test_idempotent_open(service_proxy):
    service_proxy(open=True)
    resp = service_proxy(open=True)
    # Still successful but message is informative.
    assert resp.success is True
    assert "already" in resp.message.lower()
    service_proxy(open=False)  # cleanup
