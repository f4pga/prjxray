N := 40
include ../fuzzer.mk

database: build/segbits_xiob33.db

build/segbits_xiob33.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 6 -o build/segbits_xiob33.rdb $$(find -name segdata_liob33.txt) $$(find -name segdata_riob33.txt)

build/segbits_xiob33.db: build/segbits_xiob33.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_xiob33.db $$(find -name segdata_liob33.txt) $$(find -name segdata_riob33.txt)

pushdb:
	${XRAY_MERGEDB} liob33 build/segbits_xiob33.db
	${XRAY_MERGEDB} riob33 build/segbits_xiob33.db
	${XRAY_MERGEDB} mask_liob33 build/mask_xiob33.db
	${XRAY_MERGEDB} mask_riob33 build/mask_xiob33.db

.PHONY: database pushdb

