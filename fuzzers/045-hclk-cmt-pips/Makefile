# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export FUZDIR=$(shell pwd)
PIP_TYPE?=hclk_cmt
PIPLIST_TCL=$(FUZDIR)/hclk_cmt_pip_list.tcl
TODO_RE=".*"
# Skipped pips:
# - PHSR PIPs are connected to PHASER sites, which are undocumented, so avoid
#   for now.
EXCLUDE_RE="(^.*LEAF)|(^.*BUFMR)|(^.*PHSR)|(^.*CLK_PLL7)|(^.*CLK_MMCM13)"

MAKETODO_FLAGS=--sides ",l" --pip-type ${PIP_TYPE} --seg-type ${PIP_TYPE} --re $(TODO_RE) --exclude-re $(EXCLUDE_RE)
N = 100

# All PIPs seem to have 2 bits. An exception is FREQ_REF which cannot be
# decoupled from the others, hence it will always have 4 bits.
FOUR_BIT_PIPS="FREQ_REF"

SPECIMENS_DEPS=build/cmt_regions.csv
A_PIPLIST=hclk_cmt.txt

include ../pip_loop.mk

.PRECIOUS: build/%.rdb

build/%.rdb: $(SPECIMENS_OK)
	$(XRAY_SEGMATCH) -c 4 -o $@.4 $(shell find build -name $(subst segbits,segdata,$(patsubst %.rdb,%.txt,$(notdir $@))))
	$(XRAY_SEGMATCH) -c 2 -o $@.2 $(shell find build -name $(subst segbits,segdata,$(patsubst %.rdb,%.txt,$(notdir $@))))
	grep    ${FOUR_BIT_PIPS} $@.4 >  $@
	grep -v ${FOUR_BIT_PIPS} $@.2 >> $@

build/%.db: build/%.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in  $< \
		--seg-fn-out $@

	# Keep a copy to track iter progress
	cp $< build/$(ITER)/$(notdir $<)

	${XRAY_MASKMERGE} $(subst segbits,mask,$@) \
		$(shell find build -name $(subst segbits,segdata,$(patsubst %.db,%.txt,$(notdir $@))))

database: build/segbits_hclk_cmt.db build/segbits_hclk_cmt_l.db
	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits_hclk_cmt*.db build/database/${XRAY_DATABASE} || true
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} hclk_cmt build/segbits_hclk_cmt.db
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} hclk_cmt_l build/segbits_hclk_cmt_l.db

build/cmt_regions.csv: output_cmt.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_cmt.tcl

pushdb: database
	${XRAY_MERGEDB} hclk_cmt build/database/${XRAY_DATABASE}/segbits_hclk_cmt.db
	${XRAY_MERGEDB} mask_hclk_cmt build/mask_hclk_cmt.db
	${XRAY_MERGEDB} hclk_cmt_l build/database/${XRAY_DATABASE}/segbits_hclk_cmt_l.db
	${XRAY_MERGEDB} mask_hclk_cmt_l build/mask_hclk_cmt_l.db

.PHONY: database pushdb
