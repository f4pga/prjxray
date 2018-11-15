# read/write width is relatively slow to resolve
# Even slower with multi bit masks...
N := 8
include ../fuzzer.mk

database: build/segbits_bramx.db

build/segbits_bramx.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_bramx.rdb $(addsuffix /segdata_bram_[lr].txt,$(SPECIMENS))

build/segbits_bramx.db: build/segbits_bramx.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@

pushdb:
	${XRAY_MERGEDB} bram_l build/segbits_bramx.db
	${XRAY_MERGEDB} bram_r build/segbits_bramx.db

.PHONY: database pushdb

