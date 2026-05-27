cmake_minimum_required(VERSION 3.0.2)
project(delivery_msgs)

find_package(catkin REQUIRED COMPONENTS
  std_msgs
  geometry_msgs
  message_generation
  actionlib_msgs
  actionlib
)

# Custom messages used across the delivery robot system
add_message_files(
  FILES
  ObstacleInfo.msg
  RobotStatus.msg
  VoiceCommand.msg
)

# Services that nodes expose for request/reply interactions
add_service_files(
  FILES
  OpenDeliveryBox.srv
  EmergencyStop.srv
)

# Actions used for long-running tasks (e.g. waypoint navigation)
add_action_files(
  FILES
  DeliveryMission.action
)

generate_messages(
  DEPENDENCIES
  std_msgs
  geometry_msgs
  actionlib_msgs
)

catkin_package(
  CATKIN_DEPENDS message_runtime std_msgs geometry_msgs actionlib_msgs
)
