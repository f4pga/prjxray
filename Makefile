CLANG_FORMAT ?= clang-format

build:
	git submodule update --init --recursive
	mkdir -p build
	cd build; cmake ..; $(MAKE)

format:
	find . -name \*.cc -and -not -path './third_party/*' -and -not -path './.git/*' -exec $(CLANG_FORMAT) -style=file -i {} \;
	find . -name \*.h -and -not -path './third_party/*' -and -not -path './.git/*' -exec $(CLANG_FORMAT) -style=file -i {} \;
	find . -name \*.py -and -not -path './third_party/*' -and -not -path './.git/*' -exec yapf -p -i {} \;
