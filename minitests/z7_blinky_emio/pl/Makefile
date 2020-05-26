# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
PART?=xc7z020clg400-1
VIVADO_PART?=$(PART)
BIT2FASM_ARGS= --part "$(XRAY_DIR)/database/$(XRAY_DATABASE)/$(PART)" --verbose

.PHONY: clean
.PRECIOUS: *.bit

clean:
	rm -rf *.fasm
	rm -rf *.bit
	rm -rf *.dcp
	rm -rf *.log
	rm -rf build-*

%.bit: %.v
	mkdir -p build-$(basename $@)
	cd build-$(basename $@) && env PROJECT_NAME=$(basename $@) VIVADO_PART=${VIVADO_PART} $(XRAY_VIVADO) -mode batch -source ../syn+par.tcl -nojournal -log ../$@.log
	rm -rf *.backup.log

%.fasm: %.bit
	$(XRAY_BIT2FASM) $(BIT2FASM_ARGS) $< > $@ || rm -rf $@
	@sort -u -o $@ $@
