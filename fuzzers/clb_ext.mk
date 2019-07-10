# Speciment count
N ?= 1

# A grep regex for SLICEM features to be skipped for SLICELs
SLICEM_FEATURES ?= "*"

# This set of variables are used to store the increment
# in the number of CLBs in case they are not enough and
# the generated database is inconsistent
CLBN ?= 0
INC ?= 50
VAR ?= "CLBN=$$(($(CLBN) + $(INC)))"
ENV_VAR ?= "CLBN=$(CLBN)"
ITER ?= 0
MAX_ITER ?= 10
FUZDIR = ${PWD}

SEGMATCH_ARGS ?=-m 2 -M 2

SEGDATAS=$(addsuffix /segdata_clbl[lm]_[lr].txt,$(SPECIMENS))

include ../fuzzer.mk

build/segbits_clbx.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} $(SEGMATCH_ARGS) -o build/segbits_clbx.rdb $(SEGDATAS)

checkdb:
	# If the database presents errors or is incomplete, the fuzzer is rerun.
	# When it reaches the maximum number of iterations it fails.
	@if [ $(ITER) -gt $(MAX_ITER) ]; then \
	    echo "Max Iterations reached. Fuzzer unsolvable."; \
	    exit 1; \
	fi
	$(MAKE) parsedb || $(MAKE) $(VAR) ITER=$$(($(ITER) + 1)) run

parsedb:
	$(foreach file, $(wildcard build/*.db), ${XRAY_PARSEDB} --strict $(file);)

database: build/segbits_clbl.db build/segbits_clbm.db

build/segbits_clbm.rdb: build/segbits_clbx.rdb
	cp $^ $@
build/segbits_clbl.rdb: build/segbits_clbx.rdb
	cat $^ | grep -E -v $(SLICEM_FEATURES) >$@

build/%.db: build/%.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} $(subst .rdb,.db,$(subst segbits,mask,$^)) $(SEGDATAS)

pushdb: checkdb
	${XRAY_MERGEDB} clbll_l build/segbits_clbl.db
	${XRAY_MERGEDB} clbll_r build/segbits_clbl.db
	${XRAY_MERGEDB} mask_clbll_l build/mask_clbl.db
	${XRAY_MERGEDB} mask_clbll_r build/mask_clbl.db
	${XRAY_MERGEDB} clblm_l build/segbits_clbm.db
	${XRAY_MERGEDB} clblm_r build/segbits_clbm.db
	${XRAY_MERGEDB} mask_clblm_l build/mask_clbm.db
	${XRAY_MERGEDB} mask_clblm_r build/mask_clbm.db

.PHONY: checkdb parsedb pushdb
