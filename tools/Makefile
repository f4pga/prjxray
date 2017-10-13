
# CXXFLAGS = -Wall -Wextra -O0 -ggdb
CXXFLAGS = -Wall -Wextra -O3

all: bitread segmatch

bitread: bitread.cc
	clang $(CXXFLAGS) -static -std=c++11 -o $@ $< -lstdc++

segmatch: segmatch.cc
	clang $(CXXFLAGS) -static -std=c++11 -o $@ $< -lstdc++

clean:
	rm -f bitread segmatch

.PHONY: all clean

