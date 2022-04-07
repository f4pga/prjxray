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
MAX_VIVADO_PROCESS ?= 4
MAX_TILES_INSTANCE ?= 300
MAX_NODES_INSTANCE ?= 30000

database: $(SPECIMENS_OK)
	true

pushdb:
	cp $(BUILD_DIR)/output/tile_type_*.json ${XRAY_FAMILY_DIR}/
	rm ${XRAY_FAMILY_DIR}/tile_type_*_site_type_*.json
	cp $(BUILD_DIR)/output/site_type_*.json ${XRAY_FAMILY_DIR}/
	cp $(BUILD_DIR)/output/tileconn.json ${XRAY_FAMILY_DIR}/$(XRAY_FABRIC)/
	cp $(BUILD_DIR)/output/node_wires.json ${XRAY_FAMILY_DIR}/$(XRAY_FABRIC)/

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@) -p=$(MAX_VIVADO_PROCESS) -t=$(MAX_TILES_INSTANCE) -n=$(MAX_NODES_INSTANCE)
	touch $@

run:
	rm -rf $(BUILD_DIR) run.${XRAY_PART}.ok
	$(MAKE) database
	$(MAKE) pushdb
	# Clean up intermediate files after successful pushdb.
	find $(BUILD_DIR) -name "*.json5" -delete
	touch ${RUN_OK}

clean:
	rm -rf ${BUILD_DIR} ${RUN_OK}

.PHONY: database pushdb run clean

