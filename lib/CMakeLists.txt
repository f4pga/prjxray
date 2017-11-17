add_library(libprjxray
	memory_mapped_file.cc)
target_include_directories(libprjxray PUBLIC "include")

if (PRJXRAY_BUILD_TESTING)
	add_executable(memory_mapped_file_test memory_mapped_file_test.cc)
	target_link_libraries(memory_mapped_file_test libprjxray gtest_main)
	add_test(NAME memory_mapped_file_test
		 COMMAND memory_mapped_file_test
		 WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/test_data)
endif()
