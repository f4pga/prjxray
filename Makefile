CLANG_FORMAT ?= clang-format-5.0
PYTHON_FORMAT ?= yapf
TCL_FORMAT ?= utils//tcl-reformat.sh

.PHONY: database format clean env

IN_ENV = if [ -e env/bin/activate ]; then . env/bin/activate; fi;
env:
	virtualenv --python=python3 --system-site-packages env
	$(IN_ENV) pip install -r requirements.txt
	ln -sf $(PWD)/prjxray env/lib/python3.*/site-packages/
	ln -sf $(PWD)/third_party/fasm/fasm.py env/lib/python3.*/site-packages/
	$(IN_ENV) python -c "import yaml" || (echo "Unable to find python-yaml" && exit 1)

build:
	git submodule update --init --recursive
	mkdir -p build
	cd build; cmake ..; $(MAKE)

database: build
	$(MAKE) -C $@

ALL_EXCLUDE = third_party .git env build

TEST_EXCLUDE = $(foreach x,$(ALL_EXCLUDE) fuzzers minitests experiments,--ignore $(x))
test: build
	# FIXME: Add C++ unit tests
	$(IN_ENV) py.test $(TEST_EXCLUDE) --doctest-modules

FIND_EXCLUDE = $(foreach x,$(ALL_EXCLUDE),-and -not -path './$(x)/*')
format:
	find . -name \*.cc $(FIND_EXCLUDE) -print0 | xargs -0 -P $$(nproc) ${CLANG_FORMAT} -style=file -i
	find . -name \*.h $(FIND_EXCLUDE) -print0 | xargs -0 -P $$(nproc) ${CLANG_FORMAT} -style=file -i
	$(IN_ENV) find . -name \*.py $(FIND_EXCLUDE) -print0 | xargs -0 -P $$(nproc) yapf -p -i
	find . -name \*.tcl $(FIND_EXCLUDE) -print0 | xargs -0 -P $$(nproc) -n 1 $(TCL_FORMAT)

checkdb:
	@for DB in database/*; do if [ -d $$DB ]; then \
		echo ; \
		echo "Checking $$DB"; \
		echo "============================"; \
		$(IN_ENV) python3 utils/checkdb.py --db-root $$DB; \
	fi; done

clean:
	$(MAKE) -C database clean
	$(MAKE) -C fuzzers clean
	rm -rf build
