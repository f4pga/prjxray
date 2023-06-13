cmake_minimum_required(VERSION 3.5.0)

project(prjxray)
option(PRJXRAY_BUILD_TESTING "" OFF)

# Add sanitizers-cmake package
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/third_party/sanitizers-cmake/cmake" ${CMAKE_MODULE_PATH})
find_package(Sanitizers)
if(NOT CMAKE_BUILD_TYPE)
	set(CMAKE_BUILD_TYPE Release CACHE STRING
		"Choose the type of build, options are: None Debug Release RelWithDebInfo MinSizeRel."
		FORCE)
endif()

# Hack for missing option in cctz
option(BUILD_TESTING "" OFF)

if(PRJXRAY_BUILD_TESTING)
	enable_testing()
endif()

add_subdirectory(third_party/googletest EXCLUDE_FROM_ALL)
add_subdirectory(third_party/gflags EXCLUDE_FROM_ALL)
add_subdirectory(third_party/cctz EXCLUDE_FROM_ALL)
add_subdirectory(third_party/abseil-cpp EXCLUDE_FROM_ALL)

include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-Wundefined-var-template" CXX_COMPILER_SUPPORTS_UNDEF_VAR)
if(${CXX_COMPILER_SUPPORTS_UNDEF_VAR})
    add_compile_options("-Wno-undefined-var-template")
endif()

option(YAML_CPP_BUILD_TESTS "" OFF)
add_subdirectory(third_party/yaml-cpp EXCLUDE_FROM_ALL)
target_include_directories(yaml-cpp PUBLIC
	$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/third_party/yaml-cpp/include>
	)

add_compile_options(-Wall -Werror)

add_subdirectory(lib)
add_subdirectory(tools)
