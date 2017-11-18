cmake_minimum_required(VERSION 3.5.0)

project(prjxray)
option(PRJXRAY_BUILD_TESTING "" ON)

set(CMAKE_CXX_FLAGS "-std=c++11 -Wall -Werror ${CMAKE_CXX_FLAGS}" )

# Hack for missing option in cctz
option(BUILD_TESTING "" OFF)


if(PRJXRAY_BUILD_TESTING)
	enable_testing()
	add_compile_options(-O0 -g)
else()
	add_compile_options(-O3)
endif()

add_subdirectory(third_party/googletest EXCLUDE_FROM_ALL)
add_subdirectory(third_party/gflags EXCLUDE_FROM_ALL)
add_subdirectory(third_party/cctz EXCLUDE_FROM_ALL)
add_subdirectory(third_party/abseil-cpp EXCLUDE_FROM_ALL)

add_subdirectory(lib)
add_subdirectory(tools)
