N ?= 5

include ../fuzzer.mk

database: build/segbits_bramx.db

build/segbits_bramx.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_bramx.rdb $(addsuffix /segdata_bram_[lr].txt,$(SPECIMENS))

build/segbits_bramx.db: build/segbits_bramx.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_bramx.rdb \
		--seg-fn-out build/segbits_bramx.unmerged.db
	python3 merge_in_use.py build/segbits_bramx.unmerged.db > build/segbits_bramx.db
	${XRAY_MASKMERGE} build/mask_bramx.db $(addsuffix /segdata_bram_[lr].txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} bram_l build/segbits_bramx.db
	${XRAY_MERGEDB} bram_r build/segbits_bramx.db
	${XRAY_MERGEDB} mask_bram_l build/mask_bramx.db
	${XRAY_MERGEDB} mask_bram_r build/mask_bramx.db

.PHONY: database pushdb
