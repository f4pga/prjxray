# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

N := 5
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: database/clbll database/clblm

pushdb: pushdb/clbll pushdb/clblm

database/%: $(SPECIMENS_OK)
	../../tools/segmatch -o seg_$(notdir $@).segbits \
			$(addsuffix /segdata_$(notdir $@).txt,$(SPECIMENS))

pushdb/%:
	bash ../../utils/mergedb.sh seg_$(notdir $@).segbits \
			../../database/$(XRAY_DATABASE)/seg_$(notdir $@).segbits

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clbll.segbits seg_clblm.segbits

.PHONY: database pushdb clean

