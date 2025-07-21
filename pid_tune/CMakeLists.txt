cmake_minimum_required(VERSION 3.5)
project(pid_tune)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(controller_msg REQUIRED)
find_package(ament_cmake_python REQUIRED)


# Install scripts
set(SCRIPTS_DIR scripts)
install(PROGRAMS
    ${SCRIPTS_DIR}/pid_tune_differential.py
    ${SCRIPTS_DIR}/pid_tune_drone_button_ui.py
    ${SCRIPTS_DIR}/pid_tune_drone_slider_ui.py
    DESTINATION lib/${PROJECT_NAME}
)

# Install launch files.
install(DIRECTORY
  resources
  launch
  DESTINATION share/${PROJECT_NAME}/
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
