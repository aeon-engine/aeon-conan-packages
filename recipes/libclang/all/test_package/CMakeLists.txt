cmake_minimum_required(VERSION 3.13.4)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(libclang)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
target_link_libraries(${PROJECT_NAME} CONAN_PKG::libclang)
