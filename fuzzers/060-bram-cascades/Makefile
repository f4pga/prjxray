MAKETODO_FLAGS=--re "BRAM_.\.BRAM_(?!LOGIC_OUTS).*"
export FUZDIR=$(shell pwd)
PIPLIST_TCL=$(FUZDIR)/bram_pip_list.tcl
PIP_TYPE?=bram_pips_int
SEG_TYPE?=bram
N = 50
SEGMATCH_FLAGS=-m 20 -M 45
include ../pip_loop.mk
#
# Specimens from current run must complete, but previous iterations may exist
database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} $(SEGMATCH_FLAGS) -o build/segbits_bram_l.rdb $(shell find build -name segdata_bram_l.txt)
	${XRAY_SEGMATCH} $(SEGMATCH_FLAGS) -o build/segbits_bram_r.rdb $(shell find build -name segdata_bram_r.txt)

	# Keep a copy to track iter progress
	# Also is pre-fixup, which drops and converts
	cp build/segbits_bram_l.rdb build/$(ITER)/segbits_bram_l.rdb
	cp build/segbits_bram_r.rdb build/$(ITER)/segbits_bram_r.rdb
	${XRAY_DBFIXUP} --db-root build \
		--verbose \
		--zero-db bits.dbf \
		--seg-fn-in build/segbits_bram_l.rdb \
		--seg-fn-out build/segbits_bram_l.db
	${XRAY_DBFIXUP} --db-root build \
		--verbose \
		--zero-db bits.dbf \
		--seg-fn-in build/segbits_bram_r.rdb \
		--seg-fn-out build/segbits_bram_r.db

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} bram_l build/segbits_bram_l.db
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} bram_r build/segbits_bram_r.db

# Final pushdb to real repo
pushdb: database
	${XRAY_MERGEDB} bram_l build/segbits_bram_l.db
	${XRAY_MERGEDB} bram_r build/segbits_bram_r.db
