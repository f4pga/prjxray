CLANG_FORMAT ?= clang-format

.PHONY: database format clean

build:
	git submodule update --init --recursive
	mkdir -p build
	cd build; cmake ..; $(MAKE)

database: build
	$(MAKE) -C $@

format:
	find . -name \*.cc -and -not -path './third_party/*' -and -not -path './.git/*' -exec $(CLANG_FORMAT) -style=file -i {} \;
	find . -name \*.h -and -not -path './third_party/*' -and -not -path './.git/*' -exec $(CLANG_FORMAT) -style=file -i {} \;
	find . -name \*.py -and -not -path './third_party/*' -and -not -path './.git/*' -exec yapf -p -i {} \;

clean:
	$(MAKE) -C database clean
	$(MAKE) -C fuzzers clean
	rm -rf build
