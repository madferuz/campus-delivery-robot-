cmake_minimum_required(VERSION 3.0.2)
project(delivery_voice_remote)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  geometry_msgs
  nav_msgs
  sensor_msgs
  delivery_msgs
)

catkin_package(
  CATKIN_DEPENDS rospy std_msgs geometry_msgs nav_msgs sensor_msgs delivery_msgs
)

catkin_install_python(PROGRAMS
  src/voice_command_node.py
  src/remote_telemetry_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
