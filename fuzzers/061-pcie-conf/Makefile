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
	$(MAKE) attrs
	$(MAKE) database
	$(MAKE) pushdb
	touch run.${XRAY_PART}.ok

clean:
	rm -rf ${BUILD_DIR} run.${XRAY_PART}.ok

.PHONY: all run clean

attrs: $(FUZDIR)/attrs.json

$(FUZDIR)/attrs.json: $(FUZDIR)/params.py
	python3 $(FUZDIR)/params.py --attrs-file $(FUZDIR)/attrs.json

# These are pins that are hard to parse as a regexp given that the port name ends with a number, which is misinterpreted
# as the index in the port bus
SPECIAL_PINS = EDTCHANNELSIN1,EDTCHANNELSIN2,EDTCHANNELSIN3,EDTCHANNELSIN4,EDTCHANNELSIN5,EDTCHANNELSIN6,EDTCHANNELSIN7,EDTCHANNELSIN8,LL2SENDASREQL1,LL2SENDENTERL1,LL2SENDENTERL23,USERCLK2,EDTCHANNELSOUT1,EDTCHANNELSOUT2,EDTCHANNELSOUT3,EDTCHANNELSOUT4,EDTCHANNELSOUT5,EDTCHANNELSOUT6,EDTCHANNELSOUT7,EDTCHANNELSOUT8

$(BUILD_DIR)/pcie_2_1_ports.csv: generate_ports.tcl
	env FILE_NAME=$(BUILD_DIR)/pcie_2_1_pins.csv ${XRAY_VIVADO} -mode batch -source generate_ports.tcl

$(BUILD_DIR)/pcie_2_1_ports.json: $(BUILD_DIR)/pcie_2_1_ports.csv
	python3 ${XRAY_UTILS_DIR}/make_ports.py $(BUILD_DIR)/pcie_2_1_pins.csv $(BUILD_DIR)/pcie_2_1_ports.json --special-pins $(SPECIAL_PINS)

database: $(BUILD_DIR)/segbits_pcie_bot.db $(BUILD_DIR)/pcie_2_1_ports.json

$(BUILD_DIR)/segbits_pcie_bot.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o $(BUILD_DIR)/segbits_pcie_bot.rdb $(addsuffix /segdata_pcie_bot.txt,$(SPECIMENS))

$(BUILD_DIR)/segbits_pcie_bot.db: $(BUILD_DIR)/segbits_pcie_bot.rdb
	${XRAY_DBFIXUP} --db-root $(BUILD_DIR) --zero-db bits.dbf \
		--seg-fn-in $(BUILD_DIR)/segbits_pcie_bot.rdb \
		--seg-fn-out $(BUILD_DIR)/segbits_pcie_bot.db
	${XRAY_MASKMERGE} $(BUILD_DIR)/mask_pcie_bot.db $(addsuffix /segdata_pcie_bot.txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} pcie_bot $(BUILD_DIR)/segbits_pcie_bot.db
	${XRAY_MERGEDB} mask_pcie_bot $(BUILD_DIR)/mask_pcie_bot.db
	mkdir -p $(CELLS_DATA_DIR)
	cp $(FUZDIR)/attrs.json $(CELLS_DATA_DIR)/pcie_2_1_attrs.json
	cp $(BUILD_DIR)/pcie_2_1_ports.json $(CELLS_DATA_DIR)/pcie_2_1_ports.json

.PHONY: database pushdb
