ALL_EXCLUDE = third_party .git env build

# Tools + Environment
IN_ENV = if [ -e env/bin/activate ]; then . env/bin/activate; fi;
env:
	virtualenv --python=python3 --system-site-packages env
	# Install prjxray
	ln -sf $(PWD)/prjxray env/lib/python3.*/site-packages/
	$(IN_ENV) python -c "import prjxray"
	# Install fasm from third_party
	$(IN_ENV) pip install --upgrade -e third_party/fasm
	# Install project dependencies
	$(IN_ENV) pip install -r requirements.txt
	# Install project's documentation dependencies
	$(IN_ENV) pip install -r docs/requirements.txt
	# Check fasm library was installed
	$(IN_ENV) python -c "import fasm"
	$(IN_ENV) python -c "import fasm.output"
	# Check YAML is installed
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
	$(IN_ENV) PYTHONPATH="$(PWD):$(PWD)/third_party/fasm:$PYTHONPATH" py.test $(TEST_EXCLUDE) --doctest-modules --junitxml=build/py_test_results.xml

test-cpp:
	mkdir -p build
	cd build && cmake -DPRJXRAY_BUILD_TESTING=ON ..
	cd build && $(MAKE) -s
	cd build && ctest --no-compress-output -T Test -C RelWithDebInfo --output-on-failure
	xsltproc .github/kokoro/ctest2junit.xsl build/Testing/*/Test.xml > build/cpp_test_results.xml

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

# Targets related to Project X-Ray databases
# ------------------------

DATABASES=artix7 kintex7 zynq7

define database

# $(1) - Database name

checkdb-$(1):
	@echo
	@echo "Checking $(1) database"
	@echo "============================"
	@$(IN_ENV) python3 utils/checkdb.py --db-root database/$(1)

formatdb-$(1):
	@echo
	@echo "Formatting $(1) database"
	@echo "============================"
	@$(IN_ENV) cd database/$(1); python3 ../../utils/sort_db.py
	@if [ -e database/Info.md ]; then $(IN_ENV) ./utils/info_md.py --keep; fi

.PHONY: checkdb-$(1) formatdb-$(1)
.NOTPARALLEL: checkdb-$(1) formatdb-$(1)

checkdb: checkdb-$(1)
formatdb: formatdb-$(1)

endef

$(foreach DB,$(DATABASES),$(eval $(call database,$(DB))))

checkdb:
	@true

formatdb:
	@true

.PHONY: checkdb formatdb

clean:
	$(MAKE) -C database clean
	$(MAKE) -C fuzzers clean
	rm -rf build

.PHONY: clean
