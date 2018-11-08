N ?= 1
DBFIXUP ?=

include fuzzer.mk

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_clblx.db $(addsuffix /segdata_clbl[lm]_[lr].txt,$(SPECIMENS))

pushdb:
	$(DBFIXUP)
	${XRAY_MERGEDB} clbll_l build/segbits_clblx.db
	${XRAY_MERGEDB} clbll_r build/segbits_clblx.db
	${XRAY_MERGEDB} clblm_l build/segbits_clblx.db
	${XRAY_MERGEDB} clblm_r build/segbits_clblx.db

.PHONY: database pushdb

