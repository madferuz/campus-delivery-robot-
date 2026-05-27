# bag/

This directory holds **rosbag** recordings of demo sessions. It is **mandatory** that the team commits at least one bag file before final submission so the instructor can replay an end-to-end mission without rebuilding the simulation.

## How to record

Option A — using the launch file (writes directly into this directory):

```bash
roslaunch delivery_robot_bringup record_session.launch bag_prefix:=demo_run1
```

Option B — using the CLI wrapper:

```bash
delivery-cli bag start --name demo_run1 -o bag/
# ... drive a mission ...
delivery-cli bag stop -o bag/
```

## What gets recorded

See `src/delivery_robot_bringup/launch/record_session.launch` for the topic list. It captures every sensor input, the planning state, every `/delivery/*` topic and the move_base feedback so a replay reconstructs both perception and decisions.

## How to inspect or replay

```bash
rosbag info bag/demo_run1*.bag      # metadata + topic summary
rosbag play bag/demo_run1*.bag      # full replay
delivery-cli bag list -o bag/       # quick listing with sizes
```
