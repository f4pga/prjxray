SHELL = bash
ALL_EXCLUDE = third_party .git env build docs/env

# Check if root
ifeq ($(shell id -u),0)
        $(error ERROR: Running as ID 0)
endif

# Tools + Environment
IN_ENV = if [ -e env/bin/activate ]; then . env/bin/activate; fi; source utils/environment.python.sh;
env:
	virtualenv --python=python3 env
	# Install prjxray
	ln -sf $(PWD)/prjxray env/lib/python3.*/site-packages/
	$(IN_ENV) python -c "import prjxray"
	# Install fasm from third_party
	$(IN_ENV) pip install --upgrade -e third_party/fasm
	# Install sdfparse form third party
	$(IN_ENV) pip install --upgrade -e third_party/python-sdf-timing
	# Install project dependencies
	$(IN_ENV) pip install -r requirements.txt
	# Install project's documentation dependencies
	$(IN_ENV) pip install -r docs/requirements.txt
	# Check fasm library was installed
	$(IN_ENV) python -c "import fasm"
	$(IN_ENV) python -c "import fasm.output"
	# Check sdfparse lib was installed
	$(IN_ENV) python -c "import sdf_timing"
	$(IN_ENV) python -c "import sdf_timing.sdfparse"
	# Check YAML is installed
	$(IN_ENV) python -c "import yaml" || (echo "Unable to find python-yaml" && exit 1)

build:
	git submodule update --init --recursive
	mkdir -p build
	cd build; cmake ..; $(MAKE)

.PHONY: env build

# Run tests of code.
# ------------------------
TEST_EXCLUDE = $(foreach x,$(ALL_EXCLUDE) docs fuzzers minitests experiments,--ignore $(x))

test: test-py test-cpp
	@true

test-py:
	$(IN_ENV) which py.test; py.test $(TEST_EXCLUDE) --doctest-modules --junitxml=build/py_test_results.xml

test-cpp:
	mkdir -p build
	cd build && cmake -DPRJXRAY_BUILD_TESTING=ON ..
	cd build && $(MAKE) -s
	cd build && ctest --no-compress-output -T Test -C RelWithDebInfo --output-on-failure
	xsltproc .github/kokoro/ctest2junit.xsl build/Testing/*/Test.xml > build/cpp_test_results.xml

.PHONY: test test-py test-cpp

# Run HTML test
# ------------------------

test-htmlgen:
	cd htmlgen && source htmlgen.sh

.PHONY: test-htmlgen

# Auto formatting of code.
# ------------------------
FORMAT_EXCLUDE = $(foreach x,$(ALL_EXCLUDE),-and -not -path './$(x)/*') -and -not -name *.bit

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

# Command to find and replace trailing whitespace in-place using `sed` (This is
# placed inside quotes later so need to escape the "'")
WS_CMD = sed -i '\''s@\s\+$$@@g'\''

# File filter for files to fix trailing whitespace in, this is just a couple of
# chained bash conditionals ensuring that the file (indicated by {}, provided by
# xargs later) is a file, and not a directory or link.  Also filters out .bit
# files as these are the only binary files currently tracked by Git and we don't
# want to inadvertently change these at all.
WS_FILTER = [ -f {} -a ! -L {} ] && [[ {} != *.bit ]]

# For every file piped to $(WS_FORMAT) apply the filter and perform the command,
# if a file does not match the filter, just returns true.
WS_FORMAT = xargs -P $$(nproc) -n 1 -I{} bash -c '$(WS_FILTER) && $(WS_CMD) {} || true'

format-trailing-ws:
	# Use `git ls-files` to give us a complete list of tracked files to fix
	# whitespace in; there is no point spending time processing anything that is
	# not known to Git.
	git ls-files | $(WS_FORMAT)

	# Additionally fix untracked (but not ignored) files.
	git ls-files -o --exclude-standard | $(WS_FORMAT)

format: format-cpp format-docs format-py format-tcl format-trailing-ws
	@true

.PHONY: format format-cpp format-py format-tcl format-trailing-ws

# Targets related to Project X-Ray databases
# ------------------------

DATABASES=artix7 kintex7 zynq7

define database

# $(1) - Database name

db-$(1):
	+source settings/$(1).sh && $$(MAKE) -C fuzzers

db-check-$(1):
	@echo
	@echo "Checking $(1) database"
	@echo "============================"
	@$(IN_ENV) python3 utils/checkdb.py

db-format-$(1):
	@echo
	@echo "Formatting $(1) database"
	@echo "============================"
	@$(IN_ENV) cd database/$(1); python3 ../../utils/sort_db.py
	@if [ -e database/Info.md ]; then $(IN_ENV) ./utils/info_md.py --keep; fi

.PHONY: db-$(1) db-check-$(1) db-format-$(1) db-extras-$(1) db-extras-$(1)-parts db-extras-$(1)-harness

db-extras-$(1): db-extras-$(1)-parts db-extras-$(1)-harness

db-$(1)-all: db-$(1) db-extras-$(1)-parts
	# Build harnesses after database is complete
	$$(MAKE) db-extras-$(1)-harness

db-check: db-check-$(1)
db-format: db-format-$(1)

endef

$(foreach DB,$(DATABASES),$(eval $(call database,$(DB))))

# Targets related to Project X-Ray parts
# --------------------------------------

ARTIX_PARTS=artix200t
ZYNQ_PARTS=zynq7010
KINTEX_PARTS=kintex70t

XRAY_PARTS=${ARTIX_PARTS} ${ZYNQ_PARTS} ${KINTEX_PARTS}

define multiple-parts

# $(1): PART to be used

db-part-only-$(1):
	+source settings/$(1).sh && $$(MAKE) -C fuzzers part_only

endef

$(foreach PART,$(XRAY_PARTS),$(eval $(call multiple-parts,$(PART))))


db-extras-artix7-parts: $(addprefix db-part-only-,$(ARTIX_PARTS))

db-extras-artix7-harness:
	+XRAY_PIN_00=J13 XRAY_PIN_01=J14 XRAY_PIN_02=K15 XRAY_PIN_03=K16 \
		XRAY_PART=xc7a35tftg256-1 XRAY_EQUIV_PART=xc7a50tfgg484-1 $(MAKE) -C fuzzers roi_only
	+source settings/artix200t.sh && \
		XRAY_PIN_00=V10 XRAY_PIN_01=W10 XRAY_PIN_02=Y11 XRAY_PIN_03=Y12 \
		XRAY_PART=xc7a200tsbg484-1 XRAY_EQUIV_PART=xc7a200tffg1156-1 \
		$(MAKE) -C fuzzers roi_only
	+source minitests/roi_harness/basys3-swbut.sh && $(MAKE) -C fuzzers roi_only
	+source minitests/roi_harness/arty-uart.sh && $(MAKE) -C fuzzers roi_only
	+source minitests/roi_harness/basys3-swbut.sh && \
		$(MAKE) -C minitests/roi_harness \
			HARNESS_DIR=$(XRAY_DATABASE_DIR)/artix7/harness/basys3/swbut copy
	+source minitests/roi_harness/basys3-swbut.sh && \
		$(MAKE) -C minitests/roi_harness \
			XRAY_ROIV=../roi_base_div2.v \
			HARNESS_DIR=$(XRAY_DATABASE_DIR)/artix7/harness/basys3/swbut_50 copy
	+source minitests/roi_harness/arty-uart.sh && \
		$(MAKE) -C minitests/roi_harness \
			HARNESS_DIR=$(XRAY_DATABASE_DIR)/artix7/harness/arty-a7/uart copy
	+source minitests/roi_harness/arty-pmod.sh && \
		$(MAKE) -C minitests/roi_harness \
			HARNESS_DIR=$(XRAY_DATABASE_DIR)/artix7/harness/arty-a7/pmod copy
	+source minitests/roi_harness/arty-swbut.sh && \
		$(MAKE) -C minitests/roi_harness \
			HARNESS_DIR=$(XRAY_DATABASE_DIR)/artix7/harness/arty-a7/swbut copy

db-extras-kintex7-parts:
	@true

db-extras-kintex7-harness:
	@true

db-extras-zynq7-parts: $(addprefix db-part-only-,$(ZYNQ_PARTS))

db-extras-zynq7-harness:
	@true

db-check:
	@true

db-format:
	@true

db-info:
	$(IN_ENV) ./utils/info_md.py

.PHONY: db-check db-format

clean:
	$(MAKE) -C database clean
	$(MAKE) -C fuzzers clean
	rm -rf build

.PHONY: clean
