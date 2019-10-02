add_library(libprjxray
	database.cc
	memory_mapped_file.cc
	segbits_file_reader.cc
	xilinx/bitstream_writer.cc
	xilinx/configuration_packet.cc
	xilinx/configuration_register.cc
	xilinx/configuration.cc
	xilinx/frames.cc
	# Spartan6 specific
	xilinx/spartan6/frame_address.cc
	xilinx/spartan6/global_clock_region.cc
	xilinx/spartan6/part.cc
	xilinx/spartan6/configuration_row.cc
	xilinx/spartan6/block_type.cc
	xilinx/spartan6/configuration_bus.cc
	xilinx/spartan6/configuration_column.cc
	# Series-7 specific
	xilinx/xc7series/frame_address.cc
	xilinx/xc7series/global_clock_region.cc
	xilinx/xc7series/part.cc
	xilinx/xc7series/configuration_row.cc
	xilinx/xc7series/block_type.cc
	xilinx/xc7series/configuration_bus.cc
	xilinx/xc7series/configuration_column.cc
	xilinx/xc7series/ecc.cc
)
target_include_directories(libprjxray PUBLIC "include")
target_link_libraries(libprjxray absl::optional absl::variant absl::strings absl::span absl::time yaml-cpp)

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

	add_executable(xilinx_xc7series_test
		xilinx/tests/xc7series/bitstream_reader_test.cc
		xilinx/tests/xc7series/bitstream_writer_test.cc
		xilinx/tests/xc7series/block_type_test.cc
		xilinx/tests/xc7series/configuration_bus_test.cc
		xilinx/tests/xc7series/configuration_column_test.cc
		xilinx/tests/xc7series/configuration_test.cc
		xilinx/tests/xc7series/configuration_packet_test.cc
		xilinx/tests/xc7series/crc_test.cc
		xilinx/tests/xc7series/ecc_test.cc
		xilinx/tests/xc7series/frame_address_test.cc
		xilinx/tests/xc7series/global_clock_region_test.cc
		xilinx/tests/xc7series/part_test.cc
		xilinx/tests/xc7series/row_test.cc
		xilinx/tests/xc7series/frames_test.cc)
	target_link_libraries(xilinx_xc7series_test libprjxray gtest_main)
	add_test(NAME xilinx_xc7series_test
		 COMMAND xilinx_xc7series_test
		 WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/test_data)

	add_executable(xilinx_spartan6_test
		xilinx/tests/spartan6/bitstream_reader_test.cc
		xilinx/tests/spartan6/bitstream_writer_test.cc
		xilinx/tests/spartan6/block_type_test.cc
		xilinx/tests/spartan6/configuration_bus_test.cc
		xilinx/tests/spartan6/configuration_column_test.cc
		xilinx/tests/spartan6/configuration_test.cc
		xilinx/tests/spartan6/configuration_packet_test.cc
		xilinx/tests/spartan6/frame_address_test.cc
		xilinx/tests/spartan6/global_clock_region_test.cc
		xilinx/tests/spartan6/part_test.cc
		xilinx/tests/spartan6/row_test.cc
		xilinx/tests/spartan6/frames_test.cc)
	target_link_libraries(xilinx_spartan6_test libprjxray gtest_main)
	add_test(NAME xilinx_spartan6_test
		 COMMAND xilinx_spartan6_test
		 WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/test_data)
endif()
