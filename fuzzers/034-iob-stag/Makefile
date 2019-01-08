N := 1
include ../fuzzer.mk

SEGDATAS=$(addsuffix /segdata_liob33.txt,$(SPECIMENS))

database: build/segbits_liob33.db

build/segbits_liob33.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c -1 -o build/segbits_liob33.rdb $(SEGDATAS)

build/segbits_liob33.db: build/segbits_liob33.rdb
	python3 ${XRAY_DIR}/utils/groupmask.py $^ $@
	${XRAY_MASKMERGE} build/mask_liob33.db $(SEGDATAS)

pushdb:
	${XRAY_MERGEDB} liob33 build/segbits_liob33.db
	${XRAY_MERGEDB} mask_liob33 build/mask_liob33.db

.PHONY: database pushdb

