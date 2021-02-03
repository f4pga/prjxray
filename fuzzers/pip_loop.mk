TODO_N ?= 50
# Number of spcimens
ifeq ($(QUICK),Y)
N = 1
TODO_N = 3
SEGMATCH_FLAGS?=
else
# Should be at least the -m value
N ?= 20
SEGMATCH_FLAGS?=-m 15 -M 45
endif
# Iteration number (each containing N specimens)
# Driven by int_loop.sh
ITER ?= 1
MAKETODO_FLAGS ?=--pip-type pips_int --seg-type int
SPECIMENS_DEPS ?=

BUILD_DIR ?= ${FUZDIR}/build
RUN_OK ?= run.ok

# See int_loop_check.py
# rempips took 35 iters once, so set 50 as a good start point
CHECK_ARGS ?= --zero-entries --timeout-iters 50
SPECIMENS := $(addprefix $(BUILD_DIR)/$(ITER)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
# Individual fuzzer directory, such as ~/prjxray/fuzzers/010-lutinit
export FUZDIR=$(shell pwd)
export ITER

all: database

SELF_DIR := $(dir $(lastword $(MAKEFILE_LIST)))
include $(SELF_DIR)/pip_list.mk

$(SPECIMENS_OK): $(BUILD_DIR)/todo.txt $(SPECIMENS_DEPS)
	mkdir -p $(BUILD_DIR)/$(ITER)
	+if [ -f ${FUZDIR}/generate.sh ] ; then \
			bash ${FUZDIR}/generate.sh $(subst /OK,,$@) ; \
		else \
			bash ${XRAY_DIR}/utils/top_generate.sh $(subst /OK,,$@) ; \
		fi
	touch $@

# Used 1) to see if we are done 2) pips to try in generate.tcl
$(BUILD_DIR)/todo.txt: piplist $(XRAY_DIR)/fuzzers/int_maketodo.py $(BUILD_DIR)/database/seeded
	XRAY_DATABASE_DIR=$(BUILD_DIR)/database \
		python3 $(XRAY_DIR)/fuzzers/int_maketodo.py \
		$(MAKETODO_FLAGS) |sort >$(BUILD_DIR)/todo_all.txt
	cat $(BUILD_DIR)/todo_all.txt | sort -R | head -n$(TODO_N) > $(BUILD_DIR)/todo.txt.tmp
	mv $(BUILD_DIR)/todo.txt.tmp $(BUILD_DIR)/todo.txt
	# Per iter files
	mkdir -p $(BUILD_DIR)/$(ITER)
	cp $(BUILD_DIR)/todo_all.txt $(BUILD_DIR)/todo.txt $(BUILD_DIR)/$(ITER)/
	# All in one dir for easier trending
	mkdir -p $(BUILD_DIR)/todo
	cp $(BUILD_DIR)/todo_all.txt $(BUILD_DIR)/todo/$(ITER)_all.txt

# Initial copy for first todo.txt
# Subsequent are based on updated db
$(BUILD_DIR)/database/seeded:
	mkdir -p $(BUILD_DIR)/database/${XRAY_DATABASE}
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db $(BUILD_DIR)/database/${XRAY_DATABASE}
	touch $(BUILD_DIR)/database/seeded

# FIXME: consider moving to script
run:
	$(MAKE) clean
	+env BUILD_DIR=$(BUILD_DIR) $(XRAY_DIR)/fuzzers/int_loop.sh --check-args "$(CHECK_ARGS)"
	touch $(RUN_OK)

clean:
	rm -rf $(BUILD_DIR) $(RUN_OK) todo

# Remove iteration specific files, but keep piplist.tcl output
cleaniter:
	rm -rf $(BUILD_DIR)/$(ITER) $(BUILD_DIR)/todo.txt

.PHONY: all database pushdb run clean cleaniter
