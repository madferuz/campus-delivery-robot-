cmake_minimum_required(VERSION 3.0.2)
project(delivery_mission)

find_package(catkin REQUIRED COMPONENTS
  rospy
  actionlib
  std_msgs
  geometry_msgs
  nav_msgs
  tf2_ros
  delivery_msgs
)

catkin_package(
  CATKIN_DEPENDS rospy actionlib std_msgs geometry_msgs nav_msgs tf2_ros delivery_msgs
)

catkin_install_python(PROGRAMS
  src/delivery_box_service_node.py
  src/mission_fsm_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
