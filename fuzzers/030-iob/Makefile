N := 1
include ../fuzzer.mk

SEGDATAS_L=$(addsuffix /segdata_liob33.txt,$(SPECIMENS))
SEGDATAS_R=$(addsuffix /segdata_riob33.txt,$(SPECIMENS))

database: build/segbits_liob33.db build/segbits_riob33.db

build/segbits_liob33.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_liob33.rdb $(SEGDATAS_L)

build/segbits_liob33.db: build/segbits_liob33.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_liob33.db $(SEGDATAS_L)

build/segbits_riob33.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_riob33.rdb $(SEGDATAS_R)

build/segbits_riob33.db: build/segbits_riob33.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_riob33.db $(SEGDATAS_R)

pushdb:
	${XRAY_MERGEDB} liob33 build/segbits_liob33.db
	${XRAY_MERGEDB} riob33 build/segbits_riob33.db
	${XRAY_MERGEDB} mask_liob33 build/mask_liob33.db
	${XRAY_MERGEDB} mask_riob33 build/mask_riob33.db

.PHONY: database pushdb

