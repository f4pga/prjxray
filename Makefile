CLANG_FORMAT ?= clang-format-3.9

.PHONY: database format clean env

env:
	virtualenv --python=python3 env
	. env/bin/activate; pip install -r requirements.txt
	ln -sf $(PWD)/prjxray env/lib/python3.*/site-packages/

build:
	git submodule update --init --recursive
	mkdir -p build
	cd build; cmake ..; $(MAKE)

database: build
	$(MAKE) -C $@

format:
	find . -name \*.cc -and -not -path './third_party/*' -and -not -path './.git/*' -print0 | xargs -0 -P $$(nproc) ${CLANG_FORMAT} -style=file -i
	find . -name \*.h -and -not -path './third_party/*' -and -not -path './.git/*' -print0 | xargs -0 -P $$(nproc) ${CLANG_FORMAT} -style=file -i
	find . -name \*.py -and -not -path './third_party/*' -and -not -path './.git/*' -print0 | xargs -0 -P $$(nproc) yapf -p -i
	find . -name \*.tcl -and -not -path './third_party/*' -and -not -path './.git/*' -print0 | xargs -0 -P $$(nproc) -n 1 ${XRAY_TCL_REFORMAT} 2>/dev/null

clean:
	$(MAKE) -C database clean
	$(MAKE) -C fuzzers clean
	rm -rf build
