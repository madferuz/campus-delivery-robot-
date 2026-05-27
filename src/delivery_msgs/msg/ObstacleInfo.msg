# ObstacleInfo.msg
# Published whenever an obstacle (object or pedestrian) is detected in
# front of the robot. Used by perception nodes to inform mission control
# and the automatic braking system.

Header header

# Classification of the obstacle. One of: "object", "pedestrian", "unknown".
string obstacle_type

# Estimated distance to the obstacle in meters along the robot's forward axis.
float32 distance

# Bearing in radians relative to the robot heading (positive = left).
float32 bearing

# Confidence of the detection in the range [0.0, 1.0].
float32 confidence
