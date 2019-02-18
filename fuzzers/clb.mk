SELF_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

N ?= 1
CLB_DBFIXUP ?=
# Fuzzer that can accept SLICEL data
# ie set to N if only for SLICEM
SLICEL ?= Y

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

include $(SELF_DIR)/fuzzer.mk

database: build/segbits_clbx.db

ifeq ($(SLICEL),Y)
SEGDATAS=$(addsuffix /segdata_clbl[lm]_[lr].txt,$(SPECIMENS))
else
SEGDATAS=$(addsuffix /segdata_clblm_[lr].txt,$(SPECIMENS))
endif


build/segbits_clbx.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} $(SEGMATCH_ARGS) -o build/segbits_clbx.rdb $(SEGDATAS)

build/segbits_clbx.db: build/segbits_clbx.rdb
ifeq ($(CLB_DBFIXUP),Y)
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
else
	cp $^ $@
endif
	${XRAY_MASKMERGE} build/mask_clbx.db $(SEGDATAS)

checkdb:
	# If the database presents errors or is incomplete, the fuzzer is rerun.
	# When it reaches the maximum number of iterations it fails.
	@if [ $(ITER) -gt $(MAX_ITER) ]; then \
	    echo "Max Iterations reached. Fuzzer unsolvable."; \
	    exit 1; \
	fi
	$(MAKE) parsedb || $(MAKE) $(VAR) ITER=$$(($(ITER) + 1)) run

parsedb:
	${XRAY_PARSEDB} --strict build/segbits_clbx.db

pushdb: checkdb
ifeq ($(SLICEL),Y)
	${XRAY_MERGEDB} clbll_l build/segbits_clbx.db
	${XRAY_MERGEDB} clbll_r build/segbits_clbx.db
	${XRAY_MERGEDB} mask_clbll_l build/mask_clbx.db
	${XRAY_MERGEDB} mask_clbll_r build/mask_clbx.db
endif
	${XRAY_MERGEDB} clblm_l build/segbits_clbx.db
	${XRAY_MERGEDB} clblm_r build/segbits_clbx.db
	${XRAY_MERGEDB} mask_clblm_l build/mask_clbx.db
	${XRAY_MERGEDB} mask_clblm_r build/mask_clbx.db

.PHONY: database pushdb checkdb parsedb

