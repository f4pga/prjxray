N ?= 1
DBFIXUP ?=

include ../fuzzer.mk

database: build/segbits_clbx.db

build/segbits_clbx.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_clbx.rdb $(addsuffix /segdata_clbl[lm]_[lr].txt,$(SPECIMENS))

build/segbits_clbx.db: build/segbits_clbx.rdb
ifeq ($(CLB_DBFIXUP),Y)
	${XRAY_DBFIXUP} --db_root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
else
	cp $^ $@
endif

pushdb:
	$(DBFIXUP)
	${XRAY_MERGEDB} clbll_l build/segbits_clblx.db
	${XRAY_MERGEDB} clbll_r build/segbits_clblx.db
	${XRAY_MERGEDB} clblm_l build/segbits_clblx.db
	${XRAY_MERGEDB} clblm_r build/segbits_clblx.db

.PHONY: database pushdb

