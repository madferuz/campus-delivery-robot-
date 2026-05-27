cmake_minimum_required(VERSION 3.0.2)
project(delivery_robot_bringup)

find_package(catkin REQUIRED)

catkin_package()

# Install the launch / rviz / config / world files so they end up under
# share/ where roslaunch and $(find ...) can locate them.
install(DIRECTORY launch config rviz worlds maps
        DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
        OPTIONAL)
