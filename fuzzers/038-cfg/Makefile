N = 24
include ../fuzzer.mk

database: build/segbits_cfg.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
                --seg-fn-in build/segbits_cfg.rdb \
                --seg-fn-out build/segbits_cfg.db


build/segbits_cfg.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 15 -o build/segbits_cfg.rdb $$(find -name segdata_cfg_center_mid.txt)

pushdb:
	${XRAY_MERGEDB} cfg_center_mid build/segbits_cfg.db

.PHONY: database pushdb

