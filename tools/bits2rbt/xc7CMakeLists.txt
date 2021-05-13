add_executable(bits2rbt bits2rbt.cc
	configuration_packets.cc
	header.cc
	ecc.cc)
target_link_libraries(bits2rbt absl::strings gflags)
