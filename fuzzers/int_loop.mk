SELF_DIR := $(dir $(lastword $(MAKEFILE_LIST)))
include $(SELF_DIR)/pip_loop.mk

# Specimens from current run must complete, but previous iterations may exist
database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} $(SEGMATCH_FLAGS) -o build/segbits_int_l.db $(shell find build -name segdata_int_l.txt)
	${XRAY_SEGMATCH} $(SEGMATCH_FLAGS) -o build/segbits_int_r.db $(shell find build -name segdata_int_r.txt)
	${XRAY_MASKMERGE} build/mask_clbll_l.db $(shell find build -name segdata_int_l.txt)
	${XRAY_MASKMERGE} build/mask_clbll_r.db $(shell find build -name segdata_int_r.txt)
	${XRAY_MASKMERGE} build/mask_clblm_l.db $(shell find build -name segdata_int_l.txt)
	${XRAY_MASKMERGE} build/mask_clblm_r.db $(shell find build -name segdata_int_r.txt)
	# Keep a copy to track iter progress
	# Also is pre-fixup, which drops and converts
	cp build/segbits_int_l.db build/$(ITER)/segbits_int_l.db
	cp build/segbits_int_r.db build/$(ITER)/segbits_int_r.db
# May be undersolved
# Quick doesn't do additional iters
ifneq ($(QUICK),Y)
	${XRAY_DBFIXUP} --db-root build --clb-int
	# https://github.com/SymbiFlow/prjxray/issues/399
	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} int_l build/segbits_int_l.db
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} int_r build/segbits_int_r.db
endif

# Final pushdb to real repo
pushdb:
	${XRAY_MERGEDB} int_l build/segbits_int_l.db
	${XRAY_MERGEDB} int_r build/segbits_int_r.db
	${XRAY_MERGEDB} mask_clbll_l build/mask_clbll_l.db
	${XRAY_MERGEDB} mask_clbll_r build/mask_clbll_r.db
	${XRAY_MERGEDB} mask_clblm_l build/mask_clblm_l.db
	${XRAY_MERGEDB} mask_clblm_r build/mask_clblm_r.db
