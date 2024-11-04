# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

SHELL = bash

N ?= 40

BUILD_DIR = build_${XRAY_PART}

SPECIMENS := $(addprefix ${BUILD_DIR}/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
FUZDIR ?= ${PWD}

CELLS_DATA_DIR = ${XRAY_FAMILY_DIR}/cells_data

all: database

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
SPECIAL_PINS = CLKRSVD0,CLKRSVD1,GTREFCLK0,GTREFCLK1,GTNORTHREFCLK0,GTNORTHREFCLK1,GTSOUTHREFCLK0,GTSOUTHREFCLK1,RXUSRCLK,RXUSRCLK2,TXUSRCLK,TXUSRCLK2,RXOSINTID0,PMARSVDIN0,PMARSVDIN1,PMARSVDIN2,PMARSVDIN3,PMARSVDIN4,PMARSVDOUT0,PMARSVDOUT1

$(BUILD_DIR)/gtxe2_channel_ports.csv:
	env FILE_NAME=$(BUILD_DIR)/gtxe2_channel_pins.csv ${XRAY_VIVADO} -mode batch -source generate_ports.tcl

$(BUILD_DIR)/gtxe2_channel_ports.json: $(BUILD_DIR)/gtxe2_channel_ports.csv
	python3 ${XRAY_UTILS_DIR}/make_ports.py $(BUILD_DIR)/gtxe2_channel_pins.csv $(BUILD_DIR)/gtxe2_channel_ports.json --special-pins $(SPECIAL_PINS)

database: ${BUILD_DIR}/segbits_gtx_channelx.db $(BUILD_DIR)/gtxe2_channel_ports.json

${BUILD_DIR}/segbits_gtx_channelx.rdb: $(SPECIMENS_OK)
	find ${BUILD_DIR} -name segdata_gtx_channel_\*.txt | xargs sed -i -e 's/CHANNEL_[0-3]/CHANNEL/g'
	${XRAY_SEGMATCH} -c 10 -o ${BUILD_DIR}/segbits_gtx_channelx.rdb $$(find $(SPECIMENS) -name "segdata_gtx_channel_[0123]*")

${BUILD_DIR}/segbits_gtx_channelx.db: ${BUILD_DIR}/segbits_gtx_channelx.rdb
	${XRAY_DBFIXUP} --db-root ${BUILD_DIR} --zero-db bits.dbf \
		--seg-fn-in ${BUILD_DIR}/segbits_gtx_channelx.rdb \
		--seg-fn-out ${BUILD_DIR}/segbits_gtx_channelx.db
	${XRAY_MASKMERGE} ${BUILD_DIR}/mask_gtx_channelx.db $$(find $(SPECIMENS) -name "segdata_gtx_channel_[0123]*")

pushdb:
	mkdir -p $(CELLS_DATA_DIR)
	cp attrs.json $(CELLS_DATA_DIR)/gtxe2_channel_attrs.json
	cp $(BUILD_DIR)/gtxe2_channel_ports.json $(CELLS_DATA_DIR)/gtxe2_channel_ports.json
	BUILD_DIR=$(BUILD_DIR) source pushdb.sh

.PHONY: database pushdb
