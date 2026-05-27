"""
test_voice_parser.py
====================
Pure-Python unit tests for the voice grammar used by Member 5's
voice_command_node. These run with plain `pytest` without any ROS
infrastructure - exactly what we want for fast CI loops.

Scenarios covered:
    - Recognises "deliver to <place>" sentences and pulls out the target.
    - Recognises "stop", "halt", "brake" variations.
    - Recognises "return home" and "come back".
    - Recognises "open the box" variations.
    - Rejects unrelated chatter.
"""

import os
import sys

# Add the voice_remote/src directory to sys.path so we can import the
# parser without needing a catkin install. This keeps the tests usable
# inside virtualenvs.
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(
    0,
    os.path.join(ROOT, "src", "delivery_voice_remote", "src"),
)

# Importing the script-style node module pulls in rospy, which is fine
# because parse_utterance does not call any rospy API. We try to keep
# the dependency cost low by importing the parser symbol only.
# We use importlib because the file does not have a .py-compatible
# top-level package, only a script.
import importlib.util


def _load_parser():
    spec = importlib.util.spec_from_file_location(
        "voice_command_node",
        os.path.join(ROOT, "src", "delivery_voice_remote", "src",
                     "voice_command_node.py"),
    )
    module = importlib.util.module_from_spec(spec)
    # rospy import inside the module will fail outside a catkin env, so
    # we stub it before executing.
    import types
    fake_rospy = types.SimpleNamespace(
        init_node=lambda *a, **kw: None,
        get_param=lambda name, default=None: default,
        Publisher=lambda *a, **kw: types.SimpleNamespace(publish=lambda m: None),
        Subscriber=lambda *a, **kw: None,
        loginfo=lambda *a, **kw: None,
        logwarn=lambda *a, **kw: None,
        logwarn_throttle=lambda *a, **kw: None,
        logerr=lambda *a, **kw: None,
        spin=lambda: None,
        is_shutdown=lambda: False,
        ROSInterruptException=Exception,
        Time=types.SimpleNamespace(now=lambda: 0),
    )
    sys.modules["rospy"] = fake_rospy

    # Also stub the delivery_msgs.msg and std_msgs.msg imports so the
    # module loads outside a catkin environment.
    fake_msgs = types.ModuleType("delivery_msgs")
    fake_msg_pkg = types.ModuleType("delivery_msgs.msg")
    class _Vc:  # noqa: D401 - test stub
        def __init__(self):
            self.header = types.SimpleNamespace(stamp=0)
            self.command = ""
            self.target = ""
            self.confidence = 0.0
    fake_msg_pkg.VoiceCommand = _Vc
    fake_msgs.msg = fake_msg_pkg
    sys.modules["delivery_msgs"] = fake_msgs
    sys.modules["delivery_msgs.msg"] = fake_msg_pkg

    fake_std = types.ModuleType("std_msgs")
    fake_std_msg = types.ModuleType("std_msgs.msg")
    class _String:  # noqa: D401 - test stub
        def __init__(self, data=""):
            self.data = data
    fake_std_msg.String = _String
    fake_std.msg = fake_std_msg
    sys.modules["std_msgs"] = fake_std
    sys.modules["std_msgs.msg"] = fake_std_msg

    spec.loader.exec_module(module)
    return module.parse_utterance


parse_utterance = _load_parser()


# ---------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------
class TestDeliverGrammar:

    def test_deliver_simple_target(self):
        cmd, target, conf = parse_utterance("deliver to library")
        assert cmd == "deliver"
        assert target == "library"
        assert conf > 0.5

    def test_deliver_with_article(self):
        cmd, target, _ = parse_utterance("please deliver to the gym")
        assert cmd == "deliver"
        assert target == "gym"

    def test_deliver_synonym_take(self):
        cmd, target, _ = parse_utterance("take this package to dorm_a")
        assert cmd == "deliver"
        assert target == "dorm_a"


class TestStopGrammar:

    def test_stop(self):
        cmd, _, _ = parse_utterance("STOP the robot")
        assert cmd == "stop"

    def test_halt(self):
        cmd, _, _ = parse_utterance("halt!")
        assert cmd == "stop"

    def test_brake(self):
        cmd, _, _ = parse_utterance("brake now please")
        assert cmd == "stop"


class TestReturnHomeGrammar:

    def test_return_home(self):
        cmd, _, _ = parse_utterance("return home")
        assert cmd == "return_home"

    def test_come_back(self):
        cmd, _, _ = parse_utterance("come back here")
        assert cmd == "return_home"


class TestOpenBoxGrammar:

    def test_open_box(self):
        cmd, _, _ = parse_utterance("open the box")
        assert cmd == "open_box"

    def test_open_delivery(self):
        cmd, _, _ = parse_utterance("open delivery compartment")
        assert cmd == "open_box"


class TestStatusGrammar:

    def test_status(self):
        cmd, _, _ = parse_utterance("what is your status")
        assert cmd == "status"

    def test_report(self):
        cmd, _, _ = parse_utterance("give me a report")
        assert cmd == "status"


class TestRejection:

    def test_unrelated_speech(self):
        cmd, _, conf = parse_utterance("the weather is nice today")
        assert cmd is None
        assert conf == 0.0

    def test_empty_input(self):
        cmd, _, conf = parse_utterance("")
        assert cmd is None
        assert conf == 0.0

    def test_none_input(self):
        cmd, _, conf = parse_utterance(None)
        assert cmd is None
        assert conf == 0.0
