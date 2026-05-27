#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
delivery_cli.main
=================
Owner: Member 7 (Infrastructure / CLI / Testing).

A *single* binary, ``delivery-cli``, that gives operators of the
Campus Delivery Robot a high-level, scriptable interface to every
subsystem in the stack. Built on Click, it satisfies the project's
"Advanced CLI with click library in Python (mandatory)" requirement.

Subcommand groups
-----------------
deliver
    Send the robot on a delivery mission.

stop
    Engage the emergency brake (via the EmergencyStop service).

resume
    Release the emergency brake.

box
    Open or close the delivery box (OpenDeliveryBox service).

say
    Publish a simulated voice command (std_msgs/String on
    /delivery/voice/text_in) - useful when there is no microphone on
    the demo machine.

status
    Print the latest RobotStatus.

watch
    Stream the JSON telemetry topic to stdout.

bag
    Start / stop a rosbag recording with a sensible default topic set.

list-destinations
    Show the symbolic destinations from the parameter server.

Running it::

    $ source devel/setup.bash
    $ pip install -e src/delivery_cli
    $ delivery-cli deliver library
    $ delivery-cli status --once
    $ delivery-cli bag start --name lab_demo
"""

import json
import os
import signal
import subprocess
import sys
import time
from typing import Optional

import click


# Lazy ROS import: importing rospy is slow and may pull in heavy DLLs,
# so we only do it inside subcommands that actually need a ROS master.
def _require_rospy():
    try:
        import rospy  # noqa: F401
    except ImportError:
        click.echo("rospy is not on the PYTHONPATH. Did you "
                   "`source devel/setup.bash`?", err=True)
        sys.exit(2)


# ---------------------------------------------------------------------
# Helpers that hide the rospy boilerplate from each subcommand body.
# ---------------------------------------------------------------------
def _init_node(name):
    """Initialise an anonymous rospy node for a one-shot CLI command."""
    import rospy
    rospy.init_node("delivery_cli_" + name, anonymous=True, disable_signals=True)


def _call_service(service_name, srv_type, **kwargs):
    import rospy
    rospy.wait_for_service(service_name, timeout=5.0)
    proxy = rospy.ServiceProxy(service_name, srv_type)
    return proxy(**kwargs)


# ---------------------------------------------------------------------
# Root group.
# ---------------------------------------------------------------------
@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option("1.0.0", prog_name="delivery-cli")
@click.option("--quiet", "-q", is_flag=True, default=False,
              help="Suppress non-essential output.")
@click.pass_context
def cli(ctx, quiet):
    """Campus Delivery Robot - command line operator interface."""
    ctx.ensure_object(dict)
    ctx.obj["quiet"] = quiet


# ---------------------------------------------------------------------
# deliver
# ---------------------------------------------------------------------
@cli.command()
@click.argument("destination")
@click.option("--wait/--no-wait", default=True,
              help="Block until the mission completes (default: wait).")
@click.option("--timeout", type=float, default=120.0,
              show_default=True,
              help="Maximum seconds to wait for completion.")
@click.pass_context
def deliver(ctx, destination, wait, timeout):
    """Send the robot to DESTINATION (symbolic name, e.g. 'library')."""
    _require_rospy()
    _init_node("deliver")

    import actionlib
    from geometry_msgs.msg import PoseStamped
    from delivery_msgs.msg import DeliveryMissionAction, DeliveryMissionGoal

    client = actionlib.SimpleActionClient(
        "/delivery/navigation/deliver_mission", DeliveryMissionAction)
    if not ctx.obj["quiet"]:
        click.echo("Waiting for navigation action server...")
    if not client.wait_for_server(rospy_duration(5.0)):
        click.echo("Navigation action server unavailable.", err=True)
        sys.exit(1)

    goal = DeliveryMissionGoal()
    goal.destination_name = destination
    goal.target = PoseStamped()

    if not ctx.obj["quiet"]:
        click.secho("→ dispatching mission to %s" % destination, fg="cyan")
    client.send_goal(goal)

    if not wait:
        return

    finished = client.wait_for_result(rospy_duration(timeout))
    if not finished:
        click.secho("Mission did not finish within %.0fs - cancelling."
                    % timeout, fg="yellow")
        client.cancel_goal()
        sys.exit(3)

    result = client.get_result()
    if result and result.success:
        click.secho("✓ delivered: %s (%.1f m travelled)"
                    % (result.final_state, result.total_distance_m),
                    fg="green")
    else:
        click.secho("✗ mission failed: %s"
                    % (result.final_state if result else "no result"),
                    fg="red")
        sys.exit(4)


# ---------------------------------------------------------------------
# stop / resume - safety brake controls.
# ---------------------------------------------------------------------
@cli.command()
@click.option("--reason", default="cli stop request",
              help="Free text reason logged with the stop.")
def stop(reason):
    """Engage the emergency brake via the EmergencyStop service."""
    _require_rospy()
    _init_node("stop")
    from delivery_msgs.srv import EmergencyStop
    resp = _call_service("/delivery/safety/emergency_stop",
                         EmergencyStop, engage=True, reason=reason)
    if resp.success:
        click.secho("⏹  brake engaged", fg="red", bold=True)
    else:
        click.secho("brake request failed", fg="red")
        sys.exit(1)


@cli.command()
@click.option("--reason", default="cli resume",
              help="Free text reason logged with the resume.")
def resume(reason):
    """Release the emergency brake."""
    _require_rospy()
    _init_node("resume")
    from delivery_msgs.srv import EmergencyStop
    resp = _call_service("/delivery/safety/emergency_stop",
                         EmergencyStop, engage=False, reason=reason)
    if resp.success:
        click.secho("▶  brake released", fg="green")


# ---------------------------------------------------------------------
# box - open/close the delivery lid.
# ---------------------------------------------------------------------
@cli.group()
def box():
    """Open or close the delivery box."""


@box.command("open")
def box_open():
    """Open the delivery box."""
    _require_rospy()
    _init_node("box_open")
    from delivery_msgs.srv import OpenDeliveryBox
    resp = _call_service("/delivery/box/open_delivery_box",
                         OpenDeliveryBox, open=True)
    if resp.success:
        click.secho("📦 box opened: %s" % resp.message, fg="green")
    else:
        click.secho("box open failed: %s" % resp.message, fg="red")
        sys.exit(1)


@box.command("close")
def box_close():
    """Close the delivery box."""
    _require_rospy()
    _init_node("box_close")
    from delivery_msgs.srv import OpenDeliveryBox
    resp = _call_service("/delivery/box/open_delivery_box",
                         OpenDeliveryBox, open=False)
    if resp.success:
        click.secho("📦 box closed: %s" % resp.message, fg="green")
    else:
        click.secho("box close failed: %s" % resp.message, fg="red")
        sys.exit(1)


# ---------------------------------------------------------------------
# say - publish a simulated voice utterance.
# ---------------------------------------------------------------------
@cli.command()
@click.argument("utterance", nargs=-1, required=True)
def say(utterance):
    """Publish UTTERANCE on /delivery/voice/text_in to simulate a voice."""
    _require_rospy()
    _init_node("say")
    import rospy
    from std_msgs.msg import String
    text = " ".join(utterance)
    pub = rospy.Publisher("/delivery/voice/text_in", String,
                          queue_size=1, latch=True)
    # Allow the latched message to actually leave the publisher.
    time.sleep(0.5)
    pub.publish(String(data=text))
    time.sleep(0.5)
    click.secho("🎤 said: %s" % text, fg="cyan")


# ---------------------------------------------------------------------
# status - one-shot or repeating snapshot of /delivery/status.
# ---------------------------------------------------------------------
@cli.command()
@click.option("--once/--follow", default=True,
              help="Print one snapshot (default) or follow continuously.")
@click.option("--rate", type=float, default=1.0, show_default=True,
              help="Refresh rate when following (Hz).")
def status(once, rate):
    """Show the robot's current high-level status."""
    _require_rospy()
    _init_node("status")
    import rospy
    from delivery_msgs.msg import RobotStatus

    state = {"latest": None}

    def _cb(msg):
        state["latest"] = msg

    rospy.Subscriber("/delivery/status", RobotStatus, _cb, queue_size=1)

    if once:
        # Wait up to 3 seconds for a single message.
        deadline = time.time() + 3.0
        while state["latest"] is None and time.time() < deadline:
            time.sleep(0.05)
        if state["latest"] is None:
            click.echo("no status received", err=True)
            sys.exit(1)
        _print_status(state["latest"])
        return

    period = 1.0 / max(0.1, rate)
    try:
        while not rospy.is_shutdown():
            if state["latest"] is not None:
                _print_status(state["latest"])
            time.sleep(period)
    except KeyboardInterrupt:
        pass


def _print_status(s):
    click.secho("─" * 50, fg="bright_black")
    click.echo("  state            : %s" % click.style(s.state, fg="cyan"))
    click.echo("  battery          : %.1f %%" % s.battery_percent)
    click.echo("  delivery box     : %s"
               % ("OPEN" if s.delivery_box_open else "closed"))
    click.echo("  pose (x, y)      : (%.2f, %.2f)"
               % (s.pose.position.x, s.pose.position.y))
    if s.info:
        click.echo("  info             : %s" % s.info)


# ---------------------------------------------------------------------
# watch - dump telemetry JSON.
# ---------------------------------------------------------------------
@cli.command()
@click.option("--pretty/--compact", default=True,
              help="Pretty-print JSON (default) or output compact lines.")
def watch(pretty):
    """Stream /delivery/remote/telemetry to stdout."""
    _require_rospy()
    _init_node("watch")
    import rospy
    from std_msgs.msg import String

    def _cb(msg):
        try:
            payload = json.loads(msg.data)
        except ValueError:
            click.echo(msg.data)
            return
        if pretty:
            click.echo(json.dumps(payload, indent=2, sort_keys=True))
            click.secho("─" * 50, fg="bright_black")
        else:
            click.echo(json.dumps(payload))

    rospy.Subscriber("/delivery/remote/telemetry", String, _cb,
                      queue_size=1)
    try:
        rospy.spin()
    except KeyboardInterrupt:
        pass


# ---------------------------------------------------------------------
# list-destinations
# ---------------------------------------------------------------------
@cli.command("list-destinations")
def list_destinations():
    """List symbolic destinations loaded into the navigation node."""
    _require_rospy()
    _init_node("list_destinations")
    import rospy
    dests = rospy.get_param(
        "/waypoint_action_server_node/destinations", {})
    if not dests:
        click.echo("(no destinations on parameter server)")
        return
    width = max(len(name) for name in dests)
    for name, xyz in sorted(dests.items()):
        click.echo("  %s   x=%.2f  y=%.2f  yaw=%.2f"
                   % (name.ljust(width), xyz[0], xyz[1], xyz[2]))


# ---------------------------------------------------------------------
# bag - rosbag recording helpers.
# ---------------------------------------------------------------------
DEFAULT_BAG_TOPICS = [
    "/cmd_vel",
    "/scan",
    "/odom",
    "/tf", "/tf_static",
    "/delivery/status",
    "/delivery/gps/fix",
    "/delivery/safety/brake_engaged",
    "/delivery/perception/lidar/obstacle",
    "/delivery/perception/vision/obstacles",
    "/delivery/voice/commands",
    "/delivery/remote/telemetry",
    "/delivery/navigation/plan_summary",
    "/move_base/NavfnROS/plan",
]


@cli.group()
def bag():
    """Start / stop / list rosbag recordings."""


@bag.command("start")
@click.option("--name", default="delivery_session",
              help="Bag file prefix.")
@click.option("--output-dir", "-o",
              default="bag",
              help="Directory to write the bag into.")
@click.option("--topic", "-t", multiple=True,
              help="Topic to record (repeatable). "
                   "If omitted, a sensible default set is used.")
def bag_start(name, output_dir, topic):
    """Start a rosbag recording in the background."""
    topics = list(topic) if topic else DEFAULT_BAG_TOPICS
    os.makedirs(output_dir, exist_ok=True)
    prefix = os.path.join(output_dir, name)
    cmd = ["rosbag", "record", "-O", prefix] + topics
    click.echo("→ " + " ".join(cmd))
    # Detach from CLI process - the user kills it with `bag stop` or
    # Ctrl-C in the launching terminal.
    proc = subprocess.Popen(cmd, preexec_fn=os.setsid)
    click.secho("rosbag pid %d → %s.bag" % (proc.pid, prefix), fg="green")
    # Save the pid to a small file so `bag stop` can find it.
    with open(os.path.join(output_dir, ".rosbag.pid"), "w") as fp:
        fp.write(str(proc.pid))


@bag.command("stop")
@click.option("--output-dir", "-o", default="bag",
              help="Directory containing the pid file.")
def bag_stop(output_dir):
    """Stop a background rosbag started by `bag start`."""
    pid_file = os.path.join(output_dir, ".rosbag.pid")
    if not os.path.exists(pid_file):
        click.echo("no pid file at %s" % pid_file, err=True)
        sys.exit(1)
    with open(pid_file) as fp:
        pid = int(fp.read().strip())
    try:
        os.killpg(os.getpgid(pid), signal.SIGINT)
        click.secho("⏹  rosbag pid %d signalled" % pid, fg="green")
    except ProcessLookupError:
        click.echo("rosbag pid %d not running" % pid, err=True)
    os.remove(pid_file)


@bag.command("list")
@click.option("--output-dir", "-o", default="bag",
              help="Directory to scan.")
def bag_list(output_dir):
    """List bag files in the recordings directory."""
    if not os.path.isdir(output_dir):
        click.echo("no such directory: %s" % output_dir, err=True)
        sys.exit(1)
    found = sorted(f for f in os.listdir(output_dir) if f.endswith(".bag"))
    if not found:
        click.echo("(no .bag files in %s)" % output_dir)
        return
    for name in found:
        path = os.path.join(output_dir, name)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        click.echo("  %-40s  %8.1f MB" % (name, size_mb))


# ---------------------------------------------------------------------
# Misc helpers
# ---------------------------------------------------------------------
def rospy_duration(seconds: float):
    """Wrap a float in rospy.Duration without importing at module load."""
    import rospy
    return rospy.Duration(seconds)


if __name__ == "__main__":
    cli()
