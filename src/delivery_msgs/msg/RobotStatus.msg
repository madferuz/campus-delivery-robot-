# RobotStatus.msg
# Aggregated status of the delivery robot. Published periodically by the
# mission node so that the CLI tool and the remote monitoring interface
# can show a single coherent snapshot of the robot.

Header header

# High level state machine value. One of:
#   "IDLE", "RECEIVING_COMMAND", "NAVIGATING", "AVOIDING",
#   "STOPPED_FOR_PEDESTRIAN", "AT_DESTINATION", "RETURNING", "ERROR"
string state

# Estimated battery percentage in [0.0, 100.0].
float32 battery_percent

# Current pose of the robot in the map frame.
geometry_msgs/Pose pose

# Target pose of the robot (zero if no mission active).
geometry_msgs/Pose target

# True when the delivery box is open.
bool delivery_box_open

# Free-form message for humans (e.g. "Pedestrian blocking path").
string info
