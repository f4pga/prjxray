N ?= 1
CLB_DBFIXUP ?=
# Fuzzer that can accept SLICEL data
# ie set to N if only for SLICEM
SLICEL ?= Y

include ../fuzzer.mk

database: build/segbits_clbx.db

ifeq ($(SLICEL),Y)
SEGDATAS=$(addsuffix /segdata_clbl[lm]_[lr].txt,$(SPECIMENS))
else
SEGDATAS=$(addsuffix /segdata_clblm_[lr].txt,$(SPECIMENS))
endif


build/segbits_clbx.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 2 -M 2 -o build/segbits_clbx.rdb $(SEGDATAS)

build/segbits_clbx.db: build/segbits_clbx.rdb
ifeq ($(CLB_DBFIXUP),Y)
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
else
	cp $^ $@
endif
	${XRAY_MASKMERGE} build/mask_clbx.db $(SEGDATAS)

pushdb:
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

.PHONY: database pushdb

