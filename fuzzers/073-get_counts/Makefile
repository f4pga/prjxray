# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

N := 1

BUILD_DIR = build_${XRAY_PART}
RUN_OK = run.${XRAY_PART}.ok

SPECIMENS := $(addprefix $(BUILD_DIR)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	true

pushdb:
	cp $(BUILD_DIR)/specimen_001/*.csv ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	rm -rf $(BUILD_DIR) $(RUN_OK)
	$(MAKE) database
	$(MAKE) pushdb
	touch $(RUN_OK)

clean:
	rm -rf ${BUILD_DIR} ${RUN_OK}

.PHONY: database pushdb run clean

