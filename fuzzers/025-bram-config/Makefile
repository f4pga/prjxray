# read/write width is relatively slow to resolve
# Even slower with multi bit masks...
N := 8
include ../fuzzer.mk

database: build.db_bramx.db

build.db_bramx.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build.db_bramx.rdb $(addsuffix /segdata_bram_[lr].txt,$(SPECIMENS))

build.db_bramx.db: build/segbits_bramx.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@

pushdb:
	${XRAY_MERGEDB} bram_l build.db_bramx.db
	${XRAY_MERGEDB} bram_r build.db_bramx.db

.PHONY: database pushdb

