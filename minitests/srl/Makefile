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
BIT2FASM_ARGS = --part "$(XRAY_DIR)/database/artix7/$(PART)" --verbose

VERILOG_FILES = $(wildcard *.v)
FASM_TARGETS = $(VERILOG_FILES:.v=.fasm)
SEGPRINT_TARGETS = $(VERILOG_FILES:.v=.segprint.log)

all: $(FASM_TARGETS) $(SEGPRINT_TARGETS)

clean:
	@find . -name "build-par.*" | xargs rm -rf
	@find . -name "build-syn.*" | xargs rm -rf
	@rm -f *.edif
	@rm -f *.bit
	@rm -f *.bin
	@rm -f *.bits
	@rm -f *.fasm
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
%.edif: %.v $(YOSYS)
	mkdir -p build-syn.$(basename $@)
	cd build-syn.$(basename $@) && env PROJECT_NAME=$(basename $@) $(XRAY_VIVADO) -mode batch -source ../syn.tcl -nojournal -log ../$@.log
	rm -rf *.backup.log

endif

%.bit: %.edif par.tcl
	mkdir -p build-par.$(basename $@)
	cd build-par.$(basename $@) && env PROJECT_NAME=$(basename $@) $(XRAY_VIVADO) -mode batch -source ../par.tcl -nojournal -log ../$@.log
	rm -rf *.backup.log

%.fasm: %.bit
	PYTHONPATH="$(XRAY_DIR):$(XRAY_DIR)/utils:$(XRAY_DIR)/third_party/fasm" \
    PATH="$(XRAY_DIR)/build/tools:$(PATH)" \
    $(XRAY_BIT2FASM) $(BIT2FASM_ARGS) \
        $< >$@ \
        || (rm -f $@ && exit 1)

%.unique.fasm: %.fasm
	@sort -u $< >$@

%.bits: %.bit
	$(XRAY_BITREAD) -part_file $(XRAY_DIR)/database/artix7/$(PART).yaml -o $@ -z -y $<

%.segprint.log: %.bits
	$(XRAY_SEGPRINT) -z -D -b $< > $@
