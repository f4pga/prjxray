# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# Not using clb.mk: 0-2 segmatch
# Could probably change segmatch to re though

N := 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_clbll.db $(addsuffix /segdata_clbll_[lr]_[012].txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -o build/segbits_clblm.db $(addsuffix /segdata_clblm_[lr]_[012].txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} clbll_l build/segbits_clbll.db
	${XRAY_MERGEDB} clbll_r build/segbits_clbll.db
	${XRAY_MERGEDB} clblm_l build/segbits_clblm.db
	${XRAY_MERGEDB} clblm_r build/segbits_clblm.db

$(SPECIMENS_OK):
	mkdir -p build
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

