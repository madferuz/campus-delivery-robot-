# My Contribution — Navigation & Planning

This is a **7-member group project** for the *Smart Mobility Engineering* course
at Inha University (original team repository:
[bekturtoktobekov/ROS-project-noetic](https://github.com/bekturtoktobekov/ROS-project-noetic)).
Each member owned specific ROS packages.

**My role: Navigation & Planning** — the `delivery_navigation` package. I wrote
the two nodes that turn a high-level delivery request ("go to the library") into
an executed, monitored trip to that destination.

---

## What I built

### 1. Waypoint Action Server (`waypoint_action_server_node.py`)

The mission-level navigation layer. It exposes a `DeliveryMission` **action** that
the CLI and the mission state machine call to send the robot to a destination,
and it reports live progress while the robot is en route.

Key design decisions:

- **Action, not service.** Delivery is a long-running task, so I used an
  actionlib action server rather than a one-shot service. This lets callers
  receive continuous feedback (distance remaining, percent complete) and cancel
  a mission mid-trip.
- **Delegates metric planning to `move_base`.** Rather than reimplementing path
  planning, this node acts as an orchestration layer: it forwards the resolved
  goal to `move_base` (via a `SimpleActionClient`) and supervises execution.
  This is a cleaner separation of concerns — my node owns the *mission* logic,
  `move_base` owns the *path* math.
- **Symbolic destinations.** Goals can be an explicit pose or a symbolic name
  (e.g. `library`, `cafe`) resolved against a waypoint table loaded from the
  ROS parameter server (`waypoints.yaml`).
- **Live feedback via tf2.** The node looks up the robot's current pose through
  a tf2 buffer, computes distance remaining against the goal, and publishes
  feedback at 2 Hz.
- **Robust state handling.** It maps `move_base` goal states to the project's own
  result states (`DELIVERED` / `FAILED` / `ABORTED`) and handles client
  preemption cleanly.

**ROS concepts demonstrated:** action server, action client, tf2 transforms,
parameter server, custom action messages.

### 2. Global Planner Helper (`global_planner_helper_node.py`)

A lightweight subscriber + publisher that summarizes the global plan for
downstream consumers.

- **Problem:** `move_base` publishes its full plan as a `nav_msgs/Path` with
  hundreds of poses, but the CLI and remote monitor only need a few numbers.
- **Solution:** this node subscribes to the plan, computes total path length
  (summing Euclidean distances between consecutive poses), waypoint count, and a
  validity flag, then publishes them as compact JSON on a lean topic.

**ROS concepts demonstrated:** subscriber, publisher, message transformation.

---

## How to run my part

The navigation nodes come up as part of the full system launch:

```bash
roslaunch delivery_robot_bringup delivery_robot_full.launch
```

Then send a delivery mission (via the team CLI) and watch navigation feedback:

```bash
delivery-cli deliver library
delivery-cli status --follow
```

---

## What I'd improve next

- Add a recovery behavior when `move_base` reports repeated failures, rather than
  aborting on the first failed state.
- Publish feedback based on remaining *path* length (from the plan summary) rather
  than straight-line distance, for a more accurate percent-complete.
- Unit-test the destination resolution and distance logic in isolation.
