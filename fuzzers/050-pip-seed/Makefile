# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
MAKETODO_FLAGS=--re ".*" --not-endswith ".VCC_WIRE"
ifeq ($(QUICK),Y)
N ?= 1
SEGMATCH_FLAGS=
else
N ?= 60
# Do relatively large batch to keep parallelism high
# LCM between 12 (CPUs on my system) and 16, a common CPU count
SEGMATCH_FLAGS=-m 15 -M 45
endif

CHECK_ARGS=--max-iters 12 --min-progress 50

include ../pip_loop.mk

# Specimens from current run must complete, but previous iterations may exist
database: build/segbits_int_l.db build/segbits_int_r.db build/mask_clbll_l.db build/mask_clbll_r.db build/mask_clblm_l.db build/mask_clblm_r.db
	# Keep a copy to track iter progress
	# Also is pre-fixup, which drops and converts
	cp build/segbits_int_l.db build/$(ITER)/segbits_int_l.db
	cp build/segbits_int_r.db build/$(ITER)/segbits_int_r.db
# May be undersolved
ifneq ($(QUICK),Y)
	${XRAY_DBFIXUP} --db-root build --clb-int
	# https://github.com/SymbiFlow/prjxray/issues/399
	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} int_l build/segbits_int_l.db
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} int_r build/segbits_int_r.db
endif

build/segbits_int_l.db: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} $(SEGMATCH_FLAGS) -o build/segbits_int_l.db \
		$(shell find build -name segdata_int_l.txt |sort)

build/segbits_int_r.db: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} $(SEGMATCH_FLAGS) -o build/segbits_int_r.db \
		$(shell find build -name segdata_int_r.txt |sort)

build/mask_clbll_l.db: $(SPECIMENS_OK)
	${XRAY_MASKMERGE} build/mask_clbll_l.db \
		$(shell find build -name segdata_int_l.txt |sort)

build/mask_clbll_r.db: $(SPECIMENS_OK)
	${XRAY_MASKMERGE} build/mask_clbll_r.db \
		$(shell find build -name segdata_int_r.txt |sort)

build/mask_clblm_l.db: $(SPECIMENS_OK)
	${XRAY_MASKMERGE} build/mask_clblm_l.db \
		$(shell find build -name segdata_int_l.txt |sort)

build/mask_clblm_r.db: $(SPECIMENS_OK)
	${XRAY_MASKMERGE} build/mask_clblm_r.db \
		$(shell find build -name segdata_int_r.txt |sort)

pushdb:
	${XRAY_MERGEDB} int_l build/segbits_int_l.db
	${XRAY_MERGEDB} int_r build/segbits_int_r.db
	${XRAY_MERGEDB} mask_clbll_l build/mask_clbll_l.db
	${XRAY_MERGEDB} mask_clbll_r build/mask_clbll_r.db
	${XRAY_MERGEDB} mask_clblm_l build/mask_clblm_l.db
	${XRAY_MERGEDB} mask_clblm_r build/mask_clblm_r.db
