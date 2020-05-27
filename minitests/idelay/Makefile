# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

SYNTH ?= vivado
YOSYS = $(XRAY_DIR)/third_party/yosys/yosys
PART = xc7a35tcsg324-1

VERILOG_FILES = $(wildcard *.v)
BIT_FILES = $(VERILOG_FILES:.v=.bit)

all: $(BIT_FILES)

clean:
	@find . -name "build-par.*" | xargs rm -rf
	@find . -name "build-syn.*" | xargs rm -rf
	@rm -f *.edif
	@rm -f *.bit
	@rm -f *.bin
	@rm -f *.log
	@rm -f *.dcp

help:
	@echo "Usage: make all [SYNTH=<vivado/yosys>]"

.PHONY: all clean help

$(YOSYS):
	cd $(XRAY_DIR)/third_party/yosys && make config-gcc && make -j$(shell nproc)

ifeq ($(SYNTH), yosys)
%.edif: %.v $(YOSYS)
	$(YOSYS) -p "read_verilog $< ; synth_xilinx -flatten -nosrl; write_edif -pvector bra -attrprop $@"  -l $@.log

else ifeq ($(SYNTH), vivado)
%.edif: %.v tcl/syn.tcl basys3.xdc
	mkdir -p build-syn.$(basename $@)
	cd build-syn.$(basename $@) && env PROJECT_NAME=$(basename $@) $(XRAY_VIVADO) -mode batch -source ../tcl/syn.tcl -nojournal -log ../$@.log
	rm -rf *.backup.log

endif

%.bit: %.edif tcl/par.tcl basys3.xdc
	mkdir -p build-par.$(basename $@)
	cd build-par.$(basename $@) && env PROJECT_NAME=$(basename $@) $(XRAY_VIVADO) -mode batch -source ../tcl/par.tcl -nojournal -log ../$@.log
	rm -rf *.backup.log

