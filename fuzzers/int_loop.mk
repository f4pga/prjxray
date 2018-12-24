# Number of spcimens
ifeq ($(QUICK),Y)
N ?= 1
SEGMATCH_FLAGS=
else
# Should be at least the -m value
N ?= 20
SEGMATCH_FLAGS=-m 15 -M 45
endif
# Iteration number (each containing N specimens)
# Driven by int_loop.sh
ITER ?= 1
MAKETODO_FLAGS ?=
TODO_N ?= 10
PIP_TYPE?=pips_int
PIPLIST_TCL?=$(XRAY_DIR)/fuzzers/piplist.tcl

# See int_loop_check.py
# rempips took 35 iters once, so set 50 as a good start point
CHECK_ARGS := --zero-entries --timeout-iters 50
SPECIMENS := $(addprefix build/$(ITER)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
# Individual fuzzer directory, such as ~/prjxray/fuzzers/010-lutinit
export FUZDIR=$(shell pwd)

# Specimens from current run must complete, but previous iterations may exist
database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} $(SEGMATCH_FLAGS) -o build/segbits_int_l.db $(shell find build -name segdata_int_l.txt)
	${XRAY_SEGMATCH} $(SEGMATCH_FLAGS) -o build/segbits_int_r.db $(shell find build -name segdata_int_r.txt)
	${XRAY_MASKMERGE} build/mask_clbll_l.db $(shell find build -name segdata_int_l.txt)
	${XRAY_MASKMERGE} build/mask_clbll_r.db $(shell find build -name segdata_int_r.txt)
	${XRAY_MASKMERGE} build/mask_clblm_l.db $(shell find build -name segdata_int_l.txt)
	${XRAY_MASKMERGE} build/mask_clblm_r.db $(shell find build -name segdata_int_r.txt)
	# Keep a copy to track iter progress
	# Also is pre-fixup, which drops and converts
	cp build/segbits_int_l.db build/$(ITER)/segbits_int_l.db
	cp build/segbits_int_r.db build/$(ITER)/segbits_int_r.db
# May be undersolved
ifneq ($(QUICK),Y)
	${XRAY_DBFIXUP} --db-root build --clb-int
endif

pushdb:
	${XRAY_MERGEDB} int_l build/segbits_int_l.db
	${XRAY_MERGEDB} int_r build/segbits_int_r.db
	${XRAY_MERGEDB} mask_clbll_l build/mask_clbll_l.db
	${XRAY_MERGEDB} mask_clbll_r build/mask_clbll_r.db
	${XRAY_MERGEDB} mask_clblm_l build/mask_clblm_l.db
	${XRAY_MERGEDB} mask_clblm_r build/mask_clblm_r.db

$(SPECIMENS_OK): build/todo.txt
	mkdir -p build/$(ITER)
	bash ${XRAY_DIR}/utils/top_generate.sh $(subst /OK,,$@)
	touch $@

build/$(PIP_TYPE)_l.txt: $(XRAY_DIR)/fuzzers/piplist.tcl
	mkdir -p build/$(ITER)
	cd build && vivado -mode batch -source $(PIPLIST_TCL)

# Used 1) to see if we are done 2) pips to try in generate.tcl
build/todo.txt: build/$(PIP_TYPE)_l.txt $(XRAY_DIR)/fuzzers/int_maketodo.py
	python3 $(XRAY_DIR)/fuzzers/int_maketodo.py --pip-type $(PIP_TYPE) $(MAKETODO_FLAGS) |sort >build/todo_all.txt
	cat build/todo_all.txt | sort -R | head -n$(TODO_N) > build/todo.txt.tmp
	mv build/todo.txt.tmp build/todo.txt
	# Per iter files
	mkdir -p build/$(ITER)
	cp build/todo_all.txt build/todo.txt build/$(ITER)/
	# All in one dir for easier trending
	mkdir -p build/todo
	cp build/todo_all.txt build/todo/$(ITER)_all.txt

# XXX: conider moving to script
run:
	$(MAKE) clean
	XRAY_DIR=${XRAY_DIR} MAKE="$(MAKE)" QUICK=$(QUICK) $(XRAY_DIR)/fuzzers/int_loop.sh --check-args "$(CHECK_ARGS)"
	touch run.ok

clean:
	rm -rf build run.ok todo

# Remove iteration specific files, but keep piplist.tcl output
cleanprj:
	rm -rf build/$(ITER) build/todo.txt

.PHONY: database pushdb run clean cleanprj

