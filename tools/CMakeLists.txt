add_executable(bitread bitread.cc)
target_link_libraries(bitread gflags absl::strings)

add_executable(segmatch segmatch.cc)
target_link_libraries(segmatch libprjxray gflags absl::strings)
