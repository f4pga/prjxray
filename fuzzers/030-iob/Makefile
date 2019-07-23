N := 50
SPECIMENS_DEPS := build/iobanks.txt
include ../fuzzer.mk

database: build/segbits_xiob33.db

build/iobanks.txt: write_io_banks.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/write_io_banks.tcl

build/segbits_xiob33.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 12 -o build/segbits_xiob33.rdb $$(find -name segdata_liob33.txt) $$(find -name segdata_riob33.txt)

build/segbits_xiob33.db: build/segbits_xiob33.rdb process_rdb.py bits.dbf
	python3 process_rdb.py build/segbits_xiob33.rdb > build/segbits_xiob33_processed.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in build/segbits_xiob33_processed.rdb --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_xiob33.db $$(find -name segdata_liob33.txt) $$(find -name segdata_riob33.txt)

pushdb:
ifneq (${XRAY_DATABASE}, zynq7)
	${XRAY_MERGEDB} liob33 build/segbits_xiob33.db
	${XRAY_MERGEDB} mask_liob33 build/mask_xiob33.db
endif
	${XRAY_MERGEDB} riob33 build/segbits_xiob33.db
	${XRAY_MERGEDB} mask_riob33 build/mask_xiob33.db

.PHONY: database pushdb

