ifeq ($(QUICK),Y)
N := 1
else
# Do relatively large batch to keep parallelism high
# LCM between 12 (CPUs on my system) and 16, a common CPU count
N := 48
endif
# Driven by int_loop.sh
ITER := 1
# See int_loop_check.py
# Original did 200 specimins open loop
CHECK_ARGS := --max-iters 6 --stable-iters 3
SPECIMENS := $(addprefix build/$(ITER)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
# Individual fuzzer directory, such as ~/prjxray/fuzzers/010-lutinit
export FUZDIR=$(shell pwd)
MAKETODO_FLAGS=--re ".*" --not-endswith ".VCC_WIRE"

# Specimens from current run must complete, but previous iterations may exist
database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 15 -M 45 -o build/segbits_int_l.db $(shell find build -name segdata_int_l.txt)
	${XRAY_SEGMATCH} -m 15 -M 45 -o build/segbits_int_r.db $(shell find build -name segdata_int_r.txt)
	${XRAY_MASKMERGE} build/mask_clbll_l.db $(shell find build -name segdata_int_l.txt)
	${XRAY_MASKMERGE} build/mask_clbll_r.db $(shell find build -name segdata_int_r.txt)
	${XRAY_MASKMERGE} build/mask_clblm_l.db $(shell find build -name segdata_int_l.txt)
	${XRAY_MASKMERGE} build/mask_clblm_r.db $(shell find build -name segdata_int_r.txt)
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

# FIXME: move to iter dir
$(SPECIMENS_OK): build/todo.txt
	mkdir -p build/$(ITER)
	bash generate.sh $(subst /OK,,$@)
	touch $@

build/pips_int_l.txt: $(XRAY_DIR)/fuzzers/piplist.tcl
	mkdir -p build/$(ITER)
	cd build && vivado -mode batch -source $(XRAY_DIR)/fuzzers/piplist.tcl

build/todo.txt: build/pips_int_l.txt $(XRAY_DIR)/fuzzers/int_maketodo.py
# Doesn't pushdb until very end. Compare against db so far
	python3 $(XRAY_DIR)/fuzzers/int_maketodo.py --db-dir build/$(ITER) $(MAKETODO_FLAGS) >build/todo_all.txt
	cat build/todo_all.txt | sort -R > build/todo.txt.tmp
	mv build/todo.txt.tmp build/todo.txt

# XXX: conider moving to script
run:
	$(MAKE) clean
	XRAY_DIR=${XRAY_DIR} MAKE="$(MAKE)" MAKEFLAGS="$(MAKEFLAGS)" QUICK=$(QUICK) $(XRAY_DIR)/fuzzers/int_loop.sh --check-args "$(CHECK_ARGS)"
	touch run.ok

clean:
	rm -rf build run.ok todo

# Remove iteration specific files, but keep piplist.tcl output
cleanprj:
	rm -rf build/$(ITER) build/todo.txt

.PHONY: database pushdb run clean cleanprj

