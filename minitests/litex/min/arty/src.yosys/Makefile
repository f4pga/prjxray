# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export XRAY_PART = xc7a35tcsg324-1
export XRAY_PART_YAML = $(XRAY_DATABASE_DIR)/$(XRAY_DATABASE)/$(XRAY_PART).yaml
YOSYS = $(XRAY_DIR)/third_party/yosys/yosys
SOURCES = ../verilog/mem.init ../verilog/mem_1.init ../verilog/mem_2.init ../verilog/top.v ../verilog/VexRiscv_Lite.v

all: top.f2b.bit

clean:
	@rm -f *.bit
	@rm -f *.bin
	@rm -f *.bits
	@rm -f *.fasm
	@rm -f *.frames*
	@rm -f *.log
	@rm -f *.edif
	@rm -rf build

.PHONY: all clean

$(YOSYS):
	cd $(XRAY_DIR)/third_party/yosys && make config-gcc && make -j$(shell nproc)

top.edif: $(YOSYS) synth.ys $(SOURCES)
	$(YOSYS) -s synth.ys -l yosys.log

top.bit: $(VIVADO) top.edif top.xdc top.tcl
	mkdir -p build
	cd build && $(XRAY_VIVADO) -mode batch -source ../top.tcl -nojournal -tempDir build -log vivado.log -verbose
	python3 $(XRAY_UTILS_DIR)/clean_json5.py < build/iobuf_report.json5 > build/iobuf_report.json
	cp build/*.bit ./

top.fasm: top.bit
	$(XRAY_BIT2FASM) --verbose $< > $@ \
        || (rm -f top.fasm && exit 1)

top.bits: top.bit
	$(XRAY_BITREAD) -part_file $(XRAY_PART_YAML) -o top.bits -z -y top.bit

segprint.log: top.bits
	$(XRAY_SEGPRINT) -z -D -b top.bits > segprint.log

top.frames: top.fasm
	$(XRAY_FASM2FRAMES) $< $@

top.f2b.bit: top.frames
	$(XRAY_DIR)/build/tools/xc7frames2bit --output_file $@ --part_name $(XRAY_PART) --part_file $(XRAY_PART_YAML) --frm_file $<

program: top.f2b.bit
	xc3sprog -c nexys4 top.f2b.bit
