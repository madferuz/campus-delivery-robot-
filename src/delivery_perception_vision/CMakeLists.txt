cmake_minimum_required(VERSION 3.0.2)
project(delivery_perception_vision)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  sensor_msgs
  cv_bridge
  image_transport
  delivery_msgs
)

catkin_package(
  CATKIN_DEPENDS rospy std_msgs sensor_msgs cv_bridge image_transport delivery_msgs
)

# Install Python nodes so rosrun / roslaunch can find them after build.
catkin_install_python(PROGRAMS
  src/camera_publisher_node.py
  src/vision_detector_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
