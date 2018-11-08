# read/write width is relatively slow to resolve
# Even slower with multi bit masks...
N := 8
include ../fuzzer.mk

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_bramx.db $(addsuffix /segdata_bram_[lr].txt,$(SPECIMENS))
	${XRAY_DBFIXUP} --db_root build --zero-db bits.dbf --zero-tile-types bramx

pushdb:
	${XRAY_MERGEDB} bram_l build/segbits_bramx.db
	${XRAY_MERGEDB} bram_r build/segbits_bramx.db

.PHONY: database pushdb

