N ?= 1
CLB_DBFIXUP ?=
SLICEL ?= Y

include ../fuzzer.mk

database: build/segbits_clbx.db

build/segbits_clbx.rdb: $(SPECIMENS_OK)
ifeq ($(SLICEL),Y)
	${XRAY_SEGMATCH} -o build/segbits_clbx.rdb $(addsuffix /segdata_clbl[lm]_[lr].txt,$(SPECIMENS))
else
	${XRAY_SEGMATCH} -o build/segbits_clbx.rdb $(addsuffix /segdata_clblm_[lr].txt,$(SPECIMENS))
endif

build/segbits_clbx.db: build/segbits_clbx.rdb
ifeq ($(CLB_DBFIXUP),Y)
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
else
	cp $^ $@
endif

pushdb:
ifeq ($(SLICEL),Y)
	${XRAY_MERGEDB} clbll_l build/segbits_clbx.db
	${XRAY_MERGEDB} clbll_r build/segbits_clbx.db
endif
	${XRAY_MERGEDB} clblm_l build/segbits_clbx.db
	${XRAY_MERGEDB} clblm_r build/segbits_clbx.db

.PHONY: database pushdb

