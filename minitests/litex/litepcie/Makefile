# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

SHELL = bash

PART = xc7a100tfgg484-2
PROJECT_NAME = pcie
RISCV_DIR = riscv64-unknown-elf-gcc-8.1.0-2019.01.0-x86_64-linux-ubuntu14

all: $(PROJECT_NAME).fasm

clean:
	@rm -rf build
	@rm -f *.fasm

clean_litex:
	@rm -rf ${VIRTUAL_ENV}/src
	@rm -f litex-install.ok

clean_riscv:
	@rm -rf $(RISCV_DIR)
	@rm -f riscv-gcc.ok

help:
	@echo "Usage: make all"

.PHONY: clean help

litex-install.ok:
	pip install -r requirements.txt
	touch litex-install.ok

riscv-gcc.ok:
	wget -qO- https://static.dev.sifive.com/dev-tools/$(RISCV_DIR).tar.gz | tar -xz
	touch riscv-gcc.ok

build/netv2/gateware/netv2.bit: litex-install.ok riscv-gcc.ok
	export PATH=${PATH}:${PWD}/${RISCV_DIR}/bin && \
		source ${XRAY_VIVADO_SETTINGS} && \
		${VIRTUAL_ENV}/src/litex-boards/litex_boards/targets/netv2.py --with-pcie --variant a7-100 --build

$(PROJECT_NAME).fasm: build/netv2/gateware/netv2.bit
	source $(XRAY_DIR)/settings/artix7.sh && env XRAY_PART=$(PART) ${XRAY_BIT2FASM} --verbose build/netv2/gateware/netv2.bit > $(PROJECT_NAME).fasm
