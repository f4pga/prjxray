add_library(libprjxray
	database.cc
	memory_mapped_file.cc
	segbits_file_reader.cc)
target_include_directories(libprjxray PUBLIC "include")
target_link_libraries(libprjxray absl::strings)

if (PRJXRAY_BUILD_TESTING)
	add_executable(big_endian_span_test big_endian_span_test.cc)
	target_link_libraries(big_endian_span_test libprjxray gtest_main)
	add_test(NAME big_endian_span_test
		 COMMAND big_endian_span_test)

	add_executable(bit_ops_test bit_ops_test.cc)
	target_link_libraries(bit_ops_test libprjxray gtest_main)
	add_test(NAME bit_ops_test
		 COMMAND bit_ops_test)

	add_executable(memory_mapped_file_test memory_mapped_file_test.cc)
	target_link_libraries(memory_mapped_file_test libprjxray gtest_main)
	add_test(NAME memory_mapped_file_test
		 COMMAND memory_mapped_file_test
		 WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/test_data)

	add_executable(segbits_file_reader_test segbits_file_reader_test.cc)
	target_link_libraries(segbits_file_reader_test libprjxray gtest_main)
	add_test(NAME segbits_file_reader_test
		 COMMAND segbits_file_reader_test
		 WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/test_data)
endif()
