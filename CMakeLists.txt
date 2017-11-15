cmake_minimum_required(VERSION 3.5.0)

project(prjxray)

set(CMAKE_CXX_FLAGS "-std=c++11 -Wall -Werror ${CMAKE_CXX_FLAGS}")

# Hack for missing option in cctz
option(BUILD_TESTING "" OFF)

add_subdirectory(third_party/googletest)
add_subdirectory(third_party/gflags)
add_subdirectory(third_party/cctz)
add_subdirectory(third_party/abseil-cpp)

add_subdirectory(tools)
