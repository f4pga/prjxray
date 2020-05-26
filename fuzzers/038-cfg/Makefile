# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N = 24
include ../fuzzer.mk

database: build/segbits_cfg.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
                --seg-fn-in build/segbits_cfg.rdb \
                --seg-fn-out build/segbits_cfg.db
# Some of the bits in Zynq seem to be always set
# see https://github.com/SymbiFlow/prjxray/issues/746
ifeq (${XRAY_DATABASE}, zynq7)
	python3 add_constant_bits.py build/segbits_cfg.db
endif


build/segbits_cfg.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 15 -o build/segbits_cfg.rdb $$(find -name segdata_cfg_center_mid.txt)

pushdb:
	${XRAY_MERGEDB} cfg_center_mid build/segbits_cfg.db

.PHONY: database pushdb

