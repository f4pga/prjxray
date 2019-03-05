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
PIP_TYPE?=pips_int
MAKETODO_FLAGS ?=--pip-type pips_int --seg-type int
A_PIPLIST?=$(PIP_TYPE)_l.txt
PIPLIST_TCL?=$(XRAY_FUZZERS_DIR)/piplist/piplist.tcl
SPECIMENS_DEPS ?=

# See int_loop_check.py
# rempips took 35 iters once, so set 50 as a good start point
CHECK_ARGS := --zero-entries --timeout-iters 50
SPECIMENS := $(addprefix build/$(ITER)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
# Individual fuzzer directory, such as ~/prjxray/fuzzers/010-lutinit
export FUZDIR=$(shell pwd)

all: database

$(SPECIMENS_OK): build/todo.txt $(SPECIMENS_DEPS)
	mkdir -p build/$(ITER)
	if [ -f ${FUZDIR}/generate.sh ] ; then \
			bash ${FUZDIR}/generate.sh $(subst /OK,,$@) ; \
		else \
			bash ${XRAY_DIR}/utils/top_generate.sh $(subst /OK,,$@) ; \
		fi
	touch $@

$(XRAY_FUZZERS_DIR)/piplist/build/$(PIP_TYPE)/$(A_PIPLIST): $(PIPLIST_TCL)
	mkdir -p $(XRAY_FUZZERS_DIR)/piplist/build/$(PIP_TYPE)
	cd $(XRAY_FUZZERS_DIR)/piplist/build/$(PIP_TYPE) && ${XRAY_VIVADO} -mode batch -source $(PIPLIST_TCL)

# Used 1) to see if we are done 2) pips to try in generate.tcl
build/todo.txt: $(XRAY_FUZZERS_DIR)/piplist/build/$(PIP_TYPE)/$(A_PIPLIST) $(XRAY_DIR)/fuzzers/int_maketodo.py build/database/seeded
	XRAY_DATABASE_DIR=${FUZDIR}/build/database \
		python3 $(XRAY_DIR)/fuzzers/int_maketodo.py \
		$(MAKETODO_FLAGS) |sort >build/todo_all.txt
	cat build/todo_all.txt | sort -R | head -n$(TODO_N) > build/todo.txt.tmp
	mv build/todo.txt.tmp build/todo.txt
	# Per iter files
	mkdir -p build/$(ITER)
	cp build/todo_all.txt build/todo.txt build/$(ITER)/
	# All in one dir for easier trending
	mkdir -p build/todo
	cp build/todo_all.txt build/todo/$(ITER)_all.txt

# Initial copy for first todo.txt
# Subsequent are based on updated db
build/database/seeded:
	mkdir -p build/database/${XRAY_DATABASE}
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	touch build/database/seeded

# FIXME: consider moving to script
run:
	$(MAKE) clean
	+$(XRAY_DIR)/fuzzers/int_loop.sh --check-args "$(CHECK_ARGS)"
	touch run.ok

clean:
	rm -rf build run.ok todo

# Remove iteration specific files, but keep piplist.tcl output
cleaniter:
	rm -rf build/$(ITER) build/todo.txt

cleanpiplist:
	rm -rf $(XRAY_FUZZERS_DIR)/piplist/build

.PHONY: all database pushdb run clean cleaniter cleanpiplist
