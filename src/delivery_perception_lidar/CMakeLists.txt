cmake_minimum_required(VERSION 3.0.2)
project(delivery_perception_lidar)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  sensor_msgs
  geometry_msgs
  delivery_msgs
)

catkin_package(
  CATKIN_DEPENDS rospy std_msgs sensor_msgs geometry_msgs delivery_msgs
)

catkin_install_python(PROGRAMS
  src/lidar_obstacle_node.py
  src/auto_brake_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
