N := 50
include ../fuzzer.mk

database: build/segbits_xiob33.db

build/segbits_xiob33_msk.rdb: $(SPECIMENS_OK)
	#${XRAY_SEGMATCH} -c -1 -m 1 -M 1 -o build/segbits_xiob33.rdb $$(find -name segdata_*.txt)
	#python3 ~/Work/segmask.py -i build/segbits_xiob33.rdb -o build/segbits_xiob33_msk.rdb -m IN_USE
	python3 ~/Work/lms_solver.py -o build/segbits_xiob33_msk.rdb -m IN_USE $$(find -name segdata_*.txt)

build/segbits_xiob33.db: build/segbits_xiob33_msk.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_xiob33.db $$(find -name segdata_*.txt)

pushdb:
	${XRAY_MERGEDB} liob33 build/segbits_xiob33.db
	${XRAY_MERGEDB} riob33 build/segbits_xiob33.db
	${XRAY_MERGEDB} mask_liob33 build/mask_xiob33.db
	${XRAY_MERGEDB} mask_riob33 build/mask_xiob33.db

.PHONY: database pushdb

