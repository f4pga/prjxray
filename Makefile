JOBS ?= $(shell nproc)
JOBS ?= 2
CLANG_FORMAT ?= clang-format

go:
	git submodule update --init --recursive
	mkdir -p build
	cd build; cmake ..; make -j$(JOBS)

format:
	find . -name \*.cc -and -not -path './third_party/*' -exec $(CLANG_FORMAT) -style=file -i {} \;
	find . -name \*.h -and -not -path './third_party/*' -exec $(CLANG_FORMAT) -style=file -i {} \;
	find . -name \*.py -and -not -path './third_party/*' -exec autopep8 -i {} \;
