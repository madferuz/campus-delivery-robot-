cmake_minimum_required(VERSION 3.0.2)
project(delivery_localization)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  sensor_msgs
  geometry_msgs
  nav_msgs
  tf2_ros
  tf2_geometry_msgs
)

catkin_package(
  CATKIN_DEPENDS rospy std_msgs sensor_msgs geometry_msgs nav_msgs tf2_ros tf2_geometry_msgs
)

catkin_install_python(PROGRAMS
  src/gps_simulator_node.py
  src/map_tf_broadcaster_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
