cmake_minimum_required(VERSION 3.8)
project(l3xz_openmv_camera_interfaces)

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/Gpio.srv"
  "srv/GpioSet.srv"
  "srv/Ir.srv"
  "srv/Rgb.srv"
  DEPENDENCIES std_msgs
  ADD_LINTER_TESTS
)

rosidl_get_typesupport_target(cpp_typesupport_target ${PROJECT_NAME} "rosidl_typesupport_cpp")

ament_export_dependencies(rosidl_default_runtime)

ament_package()
