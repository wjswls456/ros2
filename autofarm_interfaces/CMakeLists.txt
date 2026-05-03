cmake_minimum_required(VERSION 3.8)
project(autofarm_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
#msg 코드 생성기
find_package(rosidl_default_generators REQUIRED)
#타입 위해 필요
find_package(builtin_interfaces REQUIRED)


#실제 msg 빌드 명령
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/LatencyMsg.msg"
  DEPENDENCIES builtin_interfaces
)

ament_export_dependencies(rosidl_default_runtime)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
