# read/write width is relatively slow to resolve
# Even slower with multi bit masks...
N := 8
include ../fuzzer.mk

SEGDATAS=$(addsuffix /segdata_cmt_top_r_upper_t.txt,$(SPECIMENS))

database: build/segbits_cmt_top_r_upper_t.db

build/segbits_cmt_top_r_upper_t.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_cmt_top_r_upper_t.rdb $(SEGDATAS)

build/segbits_cmt_top_r_upper_t.db: build/segbits_cmt_top_r_upper_t.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_cmt_top_r_upper_t.db $(SEGDATAS)

pushdb:
	${XRAY_MERGEDB} cmt_top_r_upper_t build/segbits_cmt_top_r_upper_t.db
	${XRAY_MERGEDB} mask_cmt_top_r_upper_t build/mask_cmt_top_r_upper_t.db

.PHONY: database pushdb

