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
PROJECT_NAME = sata
RISCV_DIR = riscv64-unknown-elf-gcc-8.1.0-2019.01.0-x86_64-linux-ubuntu14

all: $(PROJECT_NAME).fasm

clean:
	@rm -rf build*
	@rm -f *.edif
	@rm -f *.bit
	@rm -f *.bin
	@rm -f *.log
	@rm -f *.dcp
	@rm -f *.fasm

clean_litex:
	@rm -rf ${VIRTUAL_ENV}/src
	@rm -f litex-install.ok

clean_riscv:
	@rm -rf $(RISCV_DIR)
	@rm -f riscv-gcc.ok

help:
	@echo "Usage: make all [SYNTH=<vivado/yosys>]"

.PHONY: clean help

$(YOSYS):
	cd $(XRAY_DIR)/third_party/yosys && make config-gcc && make -j$(shell nproc)

litex-install.ok:
	pip install -r requirements.txt
	touch litex-install.ok

riscv-gcc.ok:
	wget -qO- https://static.dev.sifive.com/dev-tools/$(RISCV_DIR).tar.gz | tar -xz
	touch riscv-gcc.ok

build/build.ok: litex-install.ok riscv-gcc.ok
	env PATH=${PATH}:${PWD}/${RISCV_DIR}/bin ${VIRTUAL_ENV}/src/litex-boards/litex_boards/targets/nexys_video.py --with-sata --integrated-rom-size 0x10000
	touch build/build.ok

VERILOG_FILES = ./build/nexys_video/gateware/nexys_video.v \
                ${VIRTUAL_ENV}/src/pythondata-cpu-vexriscv/pythondata_cpu_vexriscv/verilog/VexRiscv.v

ifeq ($(SYNTH), yosys)
$(PROJECT_NAME).edif: $(YOSYS) build/build.ok
	$(YOSYS) -p "read_verilog $(VERILOG_FILES); techmap -map retarget.v; synth_xilinx -flatten -nosrl -nodsp; write_edif -pvector bra -attrprop $@"  -l $@.log

else ifeq ($(SYNTH), vivado)
$(PROJECT_NAME).edif: build/build.ok tcl/syn.tcl
	mkdir -p build-syn.$(basename $@)
	cd build-syn.$(basename $@) && env PART=$(PART) PROJECT_NAME=$(PROJECT_NAME) $(XRAY_VIVADO) -mode batch -source ../tcl/syn.tcl -nojournal -log ../$@.log
	rm -rf *.backup.log

endif

$(PROJECT_NAME).bit: $(PROJECT_NAME).edif tcl/par.tcl
	mkdir -p build-par.$(basename $@)
	cd build-par.$(basename $@) && env PART=$(PART) PROJECT_NAME=$(PROJECT_NAME) $(XRAY_VIVADO) -mode batch -source ../tcl/par.tcl -nojournal -log ../$@.log
	rm -rf *.backup.log

$(PROJECT_NAME).fasm: $(PROJECT_NAME).bit
	source $(XRAY_DIR)/settings/artix7_200t.sh && env XRAY_PART=$(PART) ${XRAY_BIT2FASM} --verbose $(PROJECT_NAME).bit > $(PROJECT_NAME).fasm
