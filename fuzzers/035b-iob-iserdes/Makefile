N := 50
include ../fuzzer.mk

database: build/segbits_xioi3.db

build/segbits_xioi3.rdb2: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 20 -m 1 -M 1 -o build/segbits_xioi3.rdb2 $$(find -name segdata_*.txt)

build/segbits_xioi3.rdb: build/segbits_xioi3.rdb2
	# Keep only solution for ISERDES related features.
	grep -e ".ISERDES." $^ >$@

build/segbits_xioi3.db: build/segbits_xioi3.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --groups tag_groups.txt --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_xioi3.db $$(find -name segdata_*.txt)

pushdb:
	${XRAY_MERGEDB} lioi3 build/segbits_xioi3.db
	${XRAY_MERGEDB} lioi3_tbytesrc build/segbits_xioi3.db
	${XRAY_MERGEDB} lioi3_tbyteterm build/segbits_xioi3.db
	${XRAY_MERGEDB} rioi3 build/segbits_xioi3.db
	${XRAY_MERGEDB} rioi3_tbytesrc build/segbits_xioi3.db
	${XRAY_MERGEDB} rioi3_tbyteterm build/segbits_xioi3.db
	${XRAY_MERGEDB} mask_lioi3 build/mask_xioi3.db
	${XRAY_MERGEDB} mask_lioi3_tbytesrc build/mask_xioi3.db
	${XRAY_MERGEDB} mask_lioi3_tbyteterm build/mask_xioi3.db
	${XRAY_MERGEDB} mask_rioi3 build/mask_xioi3.db
	${XRAY_MERGEDB} mask_rioi3_tbytesrc build/mask_xioi3.db
	${XRAY_MERGEDB} mask_rioi3_tbyteterm build/mask_xioi3.db

.PHONY: database pushdb

