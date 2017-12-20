JOBS ?= $(shell nproc)
JOBS ?= 2

go:
	git submodule update --init --recursive
	mkdir -p build
	cd build; cmake ..; make -j$(JOBS)
