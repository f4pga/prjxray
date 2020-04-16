# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

N := 2
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_hclk_l.db $(shell find . -name segdata_hclk_l_design_*.txt)
	${XRAY_SEGMATCH} -o build/segbits_hclk_r.db $(shell find . -name segdata_hclk_r_design_*.txt)
	${XRAY_MASKMERGE} build/mask_hclk_l.db $(shell find . -name segdata_hclk_l_design_*.txt)
	${XRAY_MASKMERGE} build/mask_hclk_r.db $(shell find . -name segdata_hclk_r_design_*.txt)

pushdb:
	${XRAY_DBFIXUP} --db-root . --clb-int
	${XRAY_MERGEDB} hclk_l build/segbits_hclk_l.db
	${XRAY_MERGEDB} hclk_r build/segbits_hclk_r.db
	${XRAY_MERGEDB} mask_hclk_l build/mask_hclk_l.db
	${XRAY_MERGEDB} mask_hclk_r build/mask_hclk_r.db

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: database pushdb run clean

