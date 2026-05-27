cmake_minimum_required(VERSION 3.0.2)
project(delivery_tests)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  delivery_msgs
)

catkin_package()

if(CATKIN_ENABLE_TESTING)
  # rostest integration: run all .test files under launch/.
  find_package(rostest REQUIRED)
  add_rostest(launch/test_voice_parser.test)
  add_rostest(launch/test_delivery_box_service.test)
endif()
