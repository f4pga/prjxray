add_executable(bitread bitread.cc)
target_link_libraries(bitread gflags absl::strings)

add_executable(segmatch segmatch.cc)
target_link_libraries(segmatch libprjxray gflags absl::strings)

add_executable(bittool bittool.cc)
target_link_libraries(bittool libprjxray gflags absl::strings absl::span)

add_executable(frame_address_decoder frame_address_decoder.cc)
target_link_libraries(frame_address_decoder libprjxray)
