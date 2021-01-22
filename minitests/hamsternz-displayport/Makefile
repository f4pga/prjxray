# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

SHELL = bash

SYNTH ?= vivado
YOSYS = $(XRAY_DIR)/third_party/yosys/yosys
PART = xc7a200tsbg484-1
PROJECT_NAME = display_port

all: $(PROJECT_NAME).fasm

clean:
	@rm -rf build*
	@rm -f *.edif
	@rm -f *.bit
	@rm -f *.bin
	@rm -f *.log
	@rm -f *.dcp
	@rm -f *.fasm

help:
	@echo "Usage: make all [SYNTH=<vivado/yosys>]"

.PHONY: clean help

$(YOSYS):
	cd $(XRAY_DIR)/third_party/yosys && make config-gcc && make -j$(shell nproc)

DISPLAY_PORT_DIR = $(XRAY_DIR)/third_party/display_port

VERILOG_FILES = $(DISPLAY_PORT_DIR)/src/test_streams/test_source.v \
	$(DISPLAY_PORT_DIR)/src/debug/seven_segment_driver.v \
	$(DISPLAY_PORT_DIR)/src/test_streams/insert_main_stream_attrbutes_four_channels.v \
	$(DISPLAY_PORT_DIR)/src/test_streams/test_source_3840_2180_YCC_422_ch2.v \
	$(DISPLAY_PORT_DIR)/src/insert_training_pattern.v \
	$(DISPLAY_PORT_DIR)/src/main_stream_processing.v \
	$(DISPLAY_PORT_DIR)/src/auxch/channel_managemnt.v \
	$(DISPLAY_PORT_DIR)/src/auxch/hotplug_decode.v \
	$(DISPLAY_PORT_DIR)/src/auxch/dp_register_decode.v \
	$(DISPLAY_PORT_DIR)/src/skew_channels.v \
	$(DISPLAY_PORT_DIR)/src/test_streams/insert_main_stream_attrbutes_two_channels.v \
	$(DISPLAY_PORT_DIR)/src/auxch/aux_channel.v \
	$(DISPLAY_PORT_DIR)/src/auxch/dp_aux_messages.v \
	$(DISPLAY_PORT_DIR)/src/auxch/aux_interface.v \
	$(DISPLAY_PORT_DIR)/src/test_streams/insert_main_stream_attrbutes_one_channel.v \
	$(DISPLAY_PORT_DIR)/src/artix7/transceiver.v \
	$(DISPLAY_PORT_DIR)/src/scrambler_reset_inserter.v \
	$(DISPLAY_PORT_DIR)/src/artix7/gtx_tx_reset_controller.v \
	$(DISPLAY_PORT_DIR)/src/idle_pattern_inserter.v \
	$(DISPLAY_PORT_DIR)/src/artix7/transceiver_bank.v \
	$(DISPLAY_PORT_DIR)/src/auxch/link_signal_mgmt.v \
	$(DISPLAY_PORT_DIR)/src/auxch/edid_decode.v \
	$(DISPLAY_PORT_DIR)/src/scrambler_all_channels.v \
	$(DISPLAY_PORT_DIR)/src/top_level_nexys_video.v

CONSTRAINT_FILES = $(DISPLAY_PORT_DIR)/constraints/NexysVideo.xdc

ifeq ($(SYNTH), yosys)
$(PROJECT_NAME).edif: $(YOSYS)
	$(YOSYS) -p "read_verilog $(VERILOG_FILES); synth_xilinx -arch xc7 -flatten -nosrl -nodsp -top top_level_nexys_video; write_edif -pvector bra -attrprop $@"  -l $@.log

else ifeq ($(SYNTH), vivado)
$(PROJECT_NAME).edif: tcl/syn.tcl
	mkdir -p build-syn.$(basename $@)
	cd build-syn.$(basename $@) && env PART=$(PART) PROJECT_NAME=$(PROJECT_NAME) VERILOG_FILES="$(VERILOG_FILES)" $(XRAY_VIVADO) -mode batch -source ../tcl/syn.tcl -nojournal -log ../$@.log
	rm -rf *.backup.log

endif

$(PROJECT_NAME).bit: $(PROJECT_NAME).edif tcl/par.tcl
	mkdir -p build-par.$(basename $@)
	cd build-par.$(basename $@) && env PART=$(PART) PROJECT_NAME=$(PROJECT_NAME) CONSTRAINT_FILES=$(CONSTRAINT_FILES) $(XRAY_VIVADO) -mode batch -source ../tcl/par.tcl -nojournal -log ../$@.log
	rm -rf *.backup.log

$(PROJECT_NAME).fasm: $(PROJECT_NAME).bit
	source $(XRAY_DIR)/settings/artix7_200t.sh && env XRAY_PART=$(PART) ${XRAY_BIT2FASM} --verbose $(PROJECT_NAME).bit > $(PROJECT_NAME).fasm
