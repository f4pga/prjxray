# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N ?= 8
GENERATE_ARGS?="--oneval 1 --design params.csv --dframe 1b --dword 0 --dbit 4"
include ../fuzzaddr/common.mk
SEGBITS=$(BUILD_DIR)/segbits_tilegrid.tdb
$(SEGBITS): $(SPECIMENS_OK)
	# multiple bits match for the changes, but all of those except the ones with addresses ending with 0x9b are known
	# and not related to GTX_INT_INTERFACE
	${XRAY_SEGMATCH} -c 6 -o $(BUILD_DIR)/segbits_tilegrid.tdb $$(find $(BUILD_DIR) -name "segdata_tilegrid.txt")
	tr ' ' '\n' < $(SEGBITS) | grep -E 'GTX|9B' | paste -d " " - - > $(SEGBITS).tmp
	mv -fv $(SEGBITS).tmp $(SEGBITS)
