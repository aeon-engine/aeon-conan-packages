cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(OPENGL_XML_REGISTRY_PATH ${CONAN_OPENGL-REGISTRY_ROOT}/xml)
configure_file(xml_paths.h.in xml_paths.h)

add_executable(example example.cpp)
set_target_properties(example PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED ON)
target_include_directories(example PUBLIC ${CMAKE_BINARY_DIR})
target_link_libraries(example ${CONAN_LIBS})
