# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

FUZDIR=$(shell pwd)
BUILD_FOLDER=build_${XRAY_PART}
BUILD_DIR=$(FUZDIR)/$(BUILD_FOLDER)
TILEGRID_TDB_DEPENDENCIES=
TILEGRID_TDB_DEPENDENCIES += iob/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += iob_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += ioi/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += monitor/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += bram/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += bram_block/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += bram_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += clb/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += clb_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += cfg/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += dsp/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += fifo_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += cfg_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += monitor_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += clk_hrow/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += clk_bufg/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += hclk_cmt/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += pll/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += hclk_ioi/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += mmcm/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += dsp_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb
GENERATE_FULL_ARGS=

# Artix7 only fuzzers
ifeq (${XRAY_DATABASE}, artix7)
TILEGRID_TDB_DEPENDENCIES += pcie/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += pcie_int_interface/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += gtp_common/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += gtp_channel/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += gtp_int_interface/$(BUILD_FOLDER)/segbits_tilegrid.tdb
endif

# Zynq7 only fuzzers
ifeq (${XRAY_DATABASE}, zynq7)
TILEGRID_TDB_DEPENDENCIES += ps7_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb
endif

# Kintex7 only fuzzers
ifeq (${XRAY_DATABASE}, kintex7)
# xc7k420t/xc7k480t have no high performance banks
ifneq (${XRAY_FABRIC}, $(filter ${XRAY_FABRIC}, xc7k480t))
TILEGRID_TDB_DEPENDENCIES += iob18/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += iob18_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += ioi18/$(BUILD_FOLDER)/segbits_tilegrid.tdb
endif

# These kintex parts give an empty design
ifneq (${XRAY_FABRIC}, $(filter ${XRAY_FABRIC}, xc7k160t xc7k325t xc7k410t xc7k480t))
TILEGRID_TDB_DEPENDENCIES += orphan_int_column/$(BUILD_FOLDER)/segbits_tilegrid.tdb
endif
endif

BASICDB_TILEGRID=$(BUILD_FOLDER)/basicdb/${XRAY_FABRIC}/tilegrid.json

database: $(BUILD_FOLDER)/tilegrid.json

pushdb: $(BUILD_FOLDER)/tilegrid.json
	cp $(BUILD_FOLDER)/tilegrid.json ${XRAY_FAMILY_DIR}/${XRAY_FABRIC}/tilegrid.json

$(BUILD_FOLDER)/tiles/tiles.txt:
	bash generate.sh $(BUILD_FOLDER)/tiles tiles

${BASICDB_TILEGRID}: generate.py $(BUILD_FOLDER)/tiles/tiles.txt
	mkdir -p $(BUILD_FOLDER)/basicdb/${XRAY_FABRIC}
	ln -sf $(XRAY_DATABASE_DIR)/$(XRAY_DATABASE)/mapping $(BUILD_FOLDER)/basicdb/
	cd $(BUILD_FOLDER) && python3 ${FUZDIR}/generate.py \
		--tiles $(BUILD_DIR)/tiles/tiles.txt \
		--pin_func $(BUILD_DIR)/tiles/pin_func.txt \
		--out ${BUILD_DIR}/basicdb/${XRAY_FABRIC}/tilegrid.json

clb/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd clb && $(MAKE)

clb_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd clb_int && $(MAKE)

cfg/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd cfg && $(MAKE)

iob/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd iob && $(MAKE)

iob18/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd iob18 && $(MAKE)

iob_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd iob_int && $(MAKE)

iob18_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd iob18_int && $(MAKE)

ioi/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd ioi && $(MAKE)

ioi18/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd ioi18 && $(MAKE)

mmcm/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd mmcm && $(MAKE)

pll/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd pll && $(MAKE)

ps7_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd ps7_int && $(MAKE)

monitor/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd monitor && $(MAKE)

monitor_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd monitor_int && $(MAKE)

bram/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd bram && $(MAKE)

bram_block/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd bram_block && $(MAKE)

bram_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd bram_int && $(MAKE)

dsp/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd dsp && $(MAKE)

dsp_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd dsp_int && $(MAKE)

fifo_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd fifo_int && $(MAKE)

cfg_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd cfg_int && $(MAKE)

orphan_int_column/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd orphan_int_column && $(MAKE)

clk_hrow/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd clk_hrow && $(MAKE)

clk_bufg/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd clk_bufg && $(MAKE)

hclk_cmt/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd hclk_cmt && $(MAKE)

hclk_ioi/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd hclk_ioi && $(MAKE)

pcie/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd pcie && $(MAKE)

pcie_int_interface/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd pcie_int_interface && $(MAKE)

gtp_common/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd gtp_common && $(MAKE)

gtp_channel/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd gtp_channel && $(MAKE)

gtp_int_interface/$(BUILD_FOLDER)/segbits_tilegrid.tdb: ${BASICDB_TILEGRID}
	cd gtp_int_interface && $(MAKE)

$(BUILD_FOLDER)/tilegrid_tdb.json: add_tdb.py $(TILEGRID_TDB_DEPENDENCIES)
	python3 add_tdb.py \
		--fn-in ${BASICDB_TILEGRID} \
		--fn-out $(BUILD_FOLDER)/tilegrid_tdb.json

$(BUILD_FOLDER)/tilegrid.json: generate_full.py $(BUILD_FOLDER)/tilegrid_tdb.json
	cd $(BUILD_FOLDER) && python3 ${FUZDIR}/generate_full.py \
        --json-in tilegrid_tdb.json --json-out ${BUILD_DIR}/tilegrid.json
run:
	$(MAKE) clean_part
	$(MAKE) database
	$(MAKE) pushdb
	touch run.${XRAY_PART}.ok

clean:
	rm -rf build_* run.*.ok
	cd clb && $(MAKE) clean
	cd clb_int && $(MAKE) clean
	cd cfg && $(MAKE) clean
	cd iob && $(MAKE) clean
	cd iob18 && $(MAKE) clean
	cd iob_int && $(MAKE) clean
	cd iob18_int && $(MAKE) clean
	cd ioi && $(MAKE) clean
	cd ioi18 && $(MAKE) clean
	cd mmcm && $(MAKE) clean
	cd pll && $(MAKE) clean
	cd ps7_int && $(MAKE) clean
	cd bram && $(MAKE) clean
	cd bram_block && $(MAKE) clean
	cd bram_int && $(MAKE) clean
	cd dsp && $(MAKE) clean
	cd dsp_int && $(MAKE) clean
	cd fifo_int && $(MAKE) clean
	cd monitor && $(MAKE) clean
	cd monitor_int && $(MAKE) clean
	cd cfg_int && $(MAKE) clean
	cd orphan_int_column && $(MAKE) clean
	cd clk_hrow && $(MAKE) clean
	cd clk_bufg && $(MAKE) clean
	cd hclk_cmt && $(MAKE) clean
	cd hclk_ioi && $(MAKE) clean
	cd pcie && $(MAKE) clean
	cd pcie_int_interface && $(MAKE) clean
	cd gtp_common && $(MAKE) clean
	cd gtp_channel && $(MAKE) clean
	cd gtp_int_interface && $(MAKE) clean

clean_part:
	rm -rf $(BUILD_FOLDER) run.${XRAY_PART}.ok
	cd clb && $(MAKE) clean_part
	cd clb_int && $(MAKE) clean_part
	cd cfg && $(MAKE) clean_part
	cd iob && $(MAKE) clean_part
	cd iob18 && $(MAKE) clean_part
	cd iob_int && $(MAKE) clean_part
	cd iob18_int && $(MAKE) clean_part
	cd ioi && $(MAKE) clean_part
	cd ioi18 && $(MAKE) clean_part
	cd mmcm && $(MAKE) clean_part
	cd pll && $(MAKE) clean_part
	cd ps7_int && $(MAKE) clean_part
	cd bram && $(MAKE) clean_part
	cd bram_block && $(MAKE) clean_part
	cd bram_int && $(MAKE) clean_part
	cd dsp && $(MAKE) clean_part
	cd dsp_int && $(MAKE) clean_part
	cd fifo_int && $(MAKE) clean_part
	cd monitor && $(MAKE) clean_part
	cd monitor_int && $(MAKE) clean_part
	cd cfg_int && $(MAKE) clean_part
	cd orphan_int_column && $(MAKE) clean_part
	cd clk_hrow && $(MAKE) clean_part
	cd clk_bufg && $(MAKE) clean_part
	cd hclk_cmt && $(MAKE) clean_part
	cd hclk_ioi && $(MAKE) clean_part
	cd pcie && $(MAKE) clean_part
	cd pcie_int_interface && $(MAKE) clean_part
	cd gtp_common && $(MAKE) clean_part
	cd gtp_channel && $(MAKE) clean_part
	cd gtp_int_interface && $(MAKE) clean_part

.PHONY: database pushdb clean clean_part run

