N := 1
include ../fuzzer.mk

database: build/segbits_liob33.db

build/segbits_liob33.rdb:
	${XRAY_SEGMATCH} -o build/segbits_liob33.rdb $(addsuffix /segdata_liob33.txt,$(SPECIMENS))

build/segbits_liob33.db: build/segbits_liob33.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@

pushdb:
	${XRAY_MERGEDB} liob33 build/segbits_liob33.db

.PHONY: database pushdb

