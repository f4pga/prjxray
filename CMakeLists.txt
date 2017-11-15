cmake_minimum_required(VERSION 3.5.0)

project(prjxray)

set(CMAKE_CXX_FLAGS "-std=c++11 -Wall -Werror ${CMAKE_CXX_FLAGS} -O3" )

# Hack for missing option in cctz
option(BUILD_TESTING "" OFF)

add_subdirectory(third_party/googletest EXCLUDE_FROM_ALL)
add_subdirectory(third_party/gflags EXCLUDE_FROM_ALL)
add_subdirectory(third_party/cctz EXCLUDE_FROM_ALL)
add_subdirectory(third_party/abseil-cpp EXCLUDE_FROM_ALL)

add_subdirectory(tools)
