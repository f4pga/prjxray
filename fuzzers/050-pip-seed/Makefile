ifeq ($(QUICK),Y)
N ?= 1
SEGMATCH_FLAGS=
else
# Do relatively large batch to keep parallelism high
# LCM between 12 (CPUs on my system) and 16, a common CPU count
N ?= 48
SEGMATCH_FLAGS=-m 15 -M 45
endif
# Driven by int_loop.sh
ITER := 1
MAKETODO_FLAGS=--re ".*" --not-endswith ".VCC_WIRE"
PIPLIST_TCL=$(XRAY_FUZZERS_DIR)/piplist/piplist.tcl
SPECIMENS := $(addprefix build/$(ITER)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
# Individual fuzzer directory, such as ~/prjxray/fuzzers/010-lutinit
export FUZDIR=$(shell pwd)

# Specimens from current run must complete, but previous iterations may exist
database: build/database

build/database: build/segbits_int_l.db build/segbits_int_r.db build/mask_clbll_l.db build/mask_clbll_r.db build/mask_clblm_l.db build/mask_clblm_r.db
	# Keep a copy to track iter progress
	# Also is pre-fixup, which drops and converts
	cp build/segbits_int_l.db build/$(ITER)/segbits_int_l.db
	cp build/segbits_int_r.db build/$(ITER)/segbits_int_r.db
# May be undersolved
ifneq ($(QUICK),Y)
	${XRAY_DBFIXUP} --db-root build --clb-int
endif
	touch build/database

build/segbits_int_l.db: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} $(SEGMATCH_FLAGS) -o build/segbits_int_l.db $(shell find build -name segdata_int_l.txt |sort)

build/segbits_int_r.db: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} $(SEGMATCH_FLAGS) -o build/segbits_int_r.db $(shell find build -name segdata_int_r.txt |sort)

build/mask_clbll_l.db: $(SPECIMENS_OK)
	${XRAY_MASKMERGE} build/mask_clbll_l.db $(shell find build -name segdata_int_l.txt |sort)

build/mask_clbll_r.db: $(SPECIMENS_OK)
	${XRAY_MASKMERGE} build/mask_clbll_r.db $(shell find build -name segdata_int_r.txt |sort)

build/mask_clblm_l.db: $(SPECIMENS_OK)
	${XRAY_MASKMERGE} build/mask_clblm_l.db $(shell find build -name segdata_int_l.txt |sort)

build/mask_clblm_r.db: $(SPECIMENS_OK)
	${XRAY_MASKMERGE} build/mask_clblm_r.db $(shell find build -name segdata_int_r.txt |sort)

pushdb:
	${XRAY_MERGEDB} int_l build/segbits_int_l.db
	${XRAY_MERGEDB} int_r build/segbits_int_r.db
	${XRAY_MERGEDB} mask_clbll_l build/mask_clbll_l.db
	${XRAY_MERGEDB} mask_clbll_r build/mask_clbll_r.db
	${XRAY_MERGEDB} mask_clblm_l build/mask_clblm_l.db
	${XRAY_MERGEDB} mask_clblm_r build/mask_clblm_r.db

$(SPECIMENS_OK): build/todo.txt
	mkdir -p build/$(ITER)
	bash generate.sh $(subst /OK,,$@)
	touch $@

$(XRAY_FUZZERS_DIR)/piplist/build/pips_int_l.txt: $(XRAY_FUZZERS_DIR)/piplist/piplist.tcl
	mkdir -p $(XRAY_FUZZERS_DIR)/piplist/build
	cd $(XRAY_FUZZERS_DIR)/piplist/build && ${XRAY_VIVADO} -mode batch -source $(PIPLIST_TCL)

build/todo.txt: $(XRAY_FUZZERS_DIR)/piplist/build/pips_int_l.txt $(XRAY_DIR)/fuzzers/int_maketodo.py
# Doesn't pushdb until very end. Compare against db so far
	mkdir -p build/$(ITER)
	python3 $(XRAY_DIR)/fuzzers/int_maketodo.py --db-dir build $(MAKETODO_FLAGS) |sort >build/todo_all.txt
	cat build/todo_all.txt | sort -R > build/todo.txt.tmp
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
	# Because 056 cannot solve IMUX and LOGIC_OUTS, force zero entries for the
	# LOGIC_OUTS or IMUX entries.
	XRAY_DIR=${XRAY_DIR} MAKE="$(MAKE)" QUICK=$(QUICK) $(XRAY_DIR)/fuzzers/int_loop.sh \
		--check-args "--max-iters 12 --min-progress 50 --zero-entries --zero-entries-filter (IMUX.*GFAN)|(FAN_ALT.*GFAN)"
	touch run.ok

clean:
	rm -rf build run.ok todo

# Remove iteration specific files, but keep piplist.tcl output
cleaniter:
	rm -rf build/$(ITER) build/todo.txt

# Remove piplist build files in piplist directory
cleanpiplist:
	rm -rf $(XRAY_FUZZERS_DIR)/piplist/build

.PHONY: database pushdb run clean cleaniter cleanpiplist
