# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

SHELL = bash

N ?= 20

BUILD_DIR = build_${XRAY_PART}

SPECIMENS := $(addprefix ${BUILD_DIR}/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
FUZDIR ?= ${PWD}

CELLS_DATA_DIR = ${XRAY_FAMILY_DIR}/cells_data

all: database

# generate.sh / top_generate.sh call make, hence the command must
# have a + before it.
$(SPECIMENS_OK): $(SPECIMENS_DEPS)
	mkdir -p ${BUILD_DIR}
	bash ${XRAY_DIR}/utils/top_generate.sh $(subst /OK,,$@)

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.${XRAY_PART}.ok

clean:
	rm -rf ${BUILD_DIR} run.${XRAY_PART}.ok

.PHONY: all run clean

# These are pins that are hard to parse as a regexp given that the port name ends with a number, which is misinterpreted
# as the index in the port bus
SPECIAL_PINS = PLLRSVD1,PLLRSVD2,GTREFCLK0,GTREFCLK1,GTGREFCLK0,GTGREFCLK1,GTEASTREFCLK0,GTEASTREFCLK1,GTWESTREFCLK0,GTWESTREFCLK1,REFCLKOUTMONITOR0,REFCLKOUTMONITOR1

$(BUILD_DIR)/gtxe2_common_ports.csv: generate_ports.tcl
	env FILE_NAME=$(BUILD_DIR)/gtxe2_common_pins.csv ${XRAY_VIVADO} -mode batch -source generate_ports.tcl

$(BUILD_DIR)/gtxe2_common_ports.json: $(BUILD_DIR)/gtxe2_common_ports.csv
	python3 ${XRAY_UTILS_DIR}/make_ports.py $(BUILD_DIR)/gtxe2_common_pins.csv $(BUILD_DIR)/gtxe2_common_ports.json --special-pins $(SPECIAL_PINS)

database: ${BUILD_DIR}/segbits_gtx_common.db $(BUILD_DIR)/gtxe2_common_ports.json

${BUILD_DIR}/segbits_gtx_common.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o ${BUILD_DIR}/segbits_gtx_common.rdb $$(find $(SPECIMENS) -name "segdata_gtx_common*")

${BUILD_DIR}/segbits_gtx_common.db: ${BUILD_DIR}/segbits_gtx_common.rdb
	${XRAY_DBFIXUP} --db-root ${BUILD_DIR} --zero-db bits.dbf \
		--seg-fn-in ${BUILD_DIR}/segbits_gtx_common.rdb \
		--seg-fn-out ${BUILD_DIR}/segbits_gtx_common.db
	${XRAY_MASKMERGE} ${BUILD_DIR}/mask_gtx_common.db $$(find $(SPECIMENS) -name "segdata_gtx_common*")

pushdb:
	mkdir -p $(CELLS_DATA_DIR)
	cp attrs.json $(CELLS_DATA_DIR)/gtxe2_common_attrs.json
	cp $(BUILD_DIR)/gtxe2_common_ports.json $(CELLS_DATA_DIR)/gtxe2_common_ports.json
	BUILD_DIR=$(BUILD_DIR) source pushdb.sh

.PHONY: database pushdb
