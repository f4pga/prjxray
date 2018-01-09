cmake_minimum_required(VERSION 3.5.0)

project(prjxray)
option(PRJXRAY_BUILD_TESTING "" OFF)

set(CMAKE_CXX_STANDARD 14)
add_compile_options(-Wall -Werror)

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

option(YAML_CPP_BUILD_TESTS "" OFF)
add_subdirectory(third_party/yaml-cpp EXCLUDE_FROM_ALL)
target_include_directories(yaml-cpp PUBLIC
	$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/third_party/yaml-cpp/include>
	)

add_subdirectory(lib)
add_subdirectory(tools)
