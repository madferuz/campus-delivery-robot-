"""
conftest.py
===========
Shared fixtures for the delivery_tests pytest suite.

These fixtures keep individual test modules small and focused. They
also make it easy to skip a whole class of tests if the developer's
machine does not have a ROS master running.
"""

import os
import time

import pytest


def pytest_addoption(parser):
    """Add a CLI option to enable / disable ROS-dependent tests."""
    parser.addoption(
        "--with-ros", action="store_true", default=False,
        help="Run tests that require a live ROS master.",
    )


def pytest_collection_modifyitems(config, items):
    """Skip ROS-dependent tests unless --with-ros is passed."""
    if config.getoption("--with-ros"):
        return
    skip_ros = pytest.mark.skip(
        reason="needs a running ROS master (use --with-ros)")
    for item in items:
        if "needs_ros" in item.keywords:
            item.add_marker(skip_ros)


@pytest.fixture(scope="session")
def ros_master_ready():
    """Verify a ROS master is reachable. Skip if not."""
    import rosgraph
    if not rosgraph.is_master_online():
        pytest.skip("No ROS master at %s"
                    % os.environ.get("ROS_MASTER_URI", "<unset>"))
    return True


@pytest.fixture
def short_wait():
    """Helper that returns a function for sleeping a small amount."""
    def _wait(seconds=0.5):
        time.sleep(seconds)
    return _wait
