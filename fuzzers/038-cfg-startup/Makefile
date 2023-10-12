# Copyright (C) 2017-2023  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N := 4
include ../fuzzer.mk

database: build/segbits_cfg_center_mid.db

build/segbits_cfg_center_mid.db: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 3 -o build/segbits_cfg_center_mid.db $$(find -name segdata_cfg_center_mid.txt)
	sed -i 's/CFG_CENTER/CFG_CENTER_MID/g' $@

pushdb:
	${XRAY_MERGEDB} cfg_center_mid build/segbits_cfg_center_mid.db

.PHONY: database pushdb

