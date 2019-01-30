ALL_EXCLUDE = third_party .git env build

# Tools + Environment
IN_ENV = if [ -e env/bin/activate ]; then . env/bin/activate; fi;
env:
	virtualenv --python=python3 --system-site-packages env
	$(IN_ENV) pip install -r requirements.txt
	$(IN_ENV) pip install -r docs/requirements.txt
	ln -sf $(PWD)/prjxray env/lib/python3.*/site-packages/
	ln -sf $(PWD)/third_party/fasm/fasm.py env/lib/python3.*/site-packages/
	$(IN_ENV) python -c "import yaml" || (echo "Unable to find python-yaml" && exit 1)

build:
	git submodule update --init --recursive
	mkdir -p build
	cd build; cmake ..; $(MAKE)

.PHONY: env build

# Run tests of code.
# ------------------------
TEST_EXCLUDE = $(foreach x,$(ALL_EXCLUDE) fuzzers minitests experiments,--ignore $(x))

test: test-py test-cpp
	@true

test-py:
	$(IN_ENV) py.test $(TEST_EXCLUDE) --doctest-modules --junitxml=build/py_test_results.xml

test-cpp:
	mkdir -p build
	cd build && cmake -DPRJXRAY_BUILD_TESTING=ON ..
	cd build && $(MAKE) -s
	cd build && ctest --no-compress-output -T Test -C RelWithDebInfo --output-on-failure

.PHONY: test test-py test-cpp

# Auto formatting of code.
# ------------------------
FORMAT_EXCLUDE = $(foreach x,$(ALL_EXCLUDE),-and -not -path './$(x)/*')

CLANG_FORMAT ?= clang-format-5.0
format-cpp:
	find . -name \*.cc $(FORMAT_EXCLUDE) -print0 | xargs -0 -P $$(nproc) ${CLANG_FORMAT} -style=file -i
	find . -name \*.h $(FORMAT_EXCLUDE) -print0 | xargs -0 -P $$(nproc) ${CLANG_FORMAT} -style=file -i

format-docs:
	./.github/update-contributing.py

PYTHON_FORMAT ?= yapf
format-py:
	$(IN_ENV) find . -name \*.py $(FORMAT_EXCLUDE) -print0 | xargs -0 -P $$(nproc) yapf -p -i

TCL_FORMAT ?= utils//tcl-reformat.sh
format-tcl:
	find . -name \*.tcl $(FORMAT_EXCLUDE) -print0 | xargs -0 -P $$(nproc) -n 1 $(TCL_FORMAT)

format: format-cpp format-docs format-py format-tcl
	@true

.PHONY: format format-cpp format-py format-tcl

# Project X-Ray database
# ------------------------

checkdb:
	@for DB in database/*; do if [ -d $$DB ]; then \
		echo ; \
		echo "Checking $$DB"; \
		echo "============================"; \
		$(IN_ENV) python3 utils/checkdb.py --db-root $$DB; \
	fi; done

formatdb:
	@for DB in database/*; do if [ -d $$DB ]; then \
		echo ; \
		echo "Formatting $$DB"; \
		echo "============================"; \
		($(IN_ENV) cd $$DB; python3 ../../utils/sort_db.py || exit 1) || exit 1; \
	fi; done
	@make checkdb
	$(IN_ENV) ./utils/info_md.py --keep

clean:
	$(MAKE) -C database clean
	$(MAKE) -C fuzzers clean
	rm -rf build
