N := 5
include ../fuzzer.mk

database: build/segbits_xiob33.db

build/segbits_xiob33.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 2 -M 2 -o build/segbits_xiob33.rdb $$(find -name segdata_*.txt)

build/segbits_xiob33.db: build/segbits_xiob33.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_xiob33.db $$(find -name segdata_*.txt)

pushdb:
	${XRAY_MERGEDB} liob33 build/segbits_xiob33.db
	${XRAY_MERGEDB} riob33 build/segbits_xiob33.db
	${XRAY_MERGEDB} mask_liob33 build/mask_xiob33.db
	${XRAY_MERGEDB} mask_riob33 build/mask_xiob33.db

.PHONY: todo database pushdb

