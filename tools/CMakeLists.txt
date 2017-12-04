add_executable(bitread bitread.cc)
target_link_libraries(bitread gflags absl::strings)

add_executable(segmatch segmatch.cc)
target_link_libraries(segmatch libprjxray gflags absl::strings)

add_executable(bittool bittool.cc)
target_link_libraries(bittool libprjxray gflags absl::strings absl::span)
