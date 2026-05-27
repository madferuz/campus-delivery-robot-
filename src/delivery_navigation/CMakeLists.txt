cmake_minimum_required(VERSION 3.0.2)
project(delivery_navigation)

find_package(catkin REQUIRED COMPONENTS
  rospy
  actionlib
  std_msgs
  geometry_msgs
  nav_msgs
  move_base_msgs
  tf2_ros
  delivery_msgs
)

catkin_package(
  CATKIN_DEPENDS rospy actionlib std_msgs geometry_msgs nav_msgs move_base_msgs tf2_ros delivery_msgs
)

catkin_install_python(PROGRAMS
  src/waypoint_action_server_node.py
  src/global_planner_helper_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
