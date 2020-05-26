# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
PART?=${XRAY_PART}
VIVADO_PART?=$(PART)

BIT2FASM_ARGS= --part "$(XRAY_DIR)/database/$(XRAY_DATABASE)/$(PART)" --verbose

DESIGN_FILES=$(wildcard design*.v)
CSV_FILES=$(subst .v,.csv,$(DESIGN_FILES))
FASM_FILES=$(subst .v,.fasm,$(DESIGN_FILES))

.PHONY: all clean designs analysis
.PRECIOUS: %.bit %.fasm %.csv

all: analysis

clean:
	@rm -rf design_*.v
	@rm -rf design_*.tcl
	@rm -rf design_*.json
	@rm -rf design_*.csv
	@rm -rf design_*.fasm
	@rm -rf design_*.bit
	@rm -rf design_*.dcp
	@rm -rf designs.ok
	@rm -rf *.log
	@rm -rf *.jou
	@rm -rf *.xml
	@for f in build-*; \
	do \
	rm -rf $$f; \
	done
	@rm -rf .Xil
	@rm -rf snippets
	@rm -rf features.csv
	@rm -rf results.json
	@rm -rf unknown_bits.jl
	@rm -rf iobs-$(PART).csv

iobs-$(PART).csv: ../dump_iobs.tcl
	env PART=$(PART) $(XRAY_VIVADO) -mode batch -source ../dump_iobs.tcl -nojournal -log dump_iobs.log

designs.ok: iobs-$(PART).csv generate.py
	env PART=$(PART) python3 ./generate.py
	touch designs.ok

designs: designs.ok

%.bit: %.v designs.ok ../syn+par.tcl
	mkdir -p build-$(basename $@)
	cd build-$(basename $@) && env PROJECT_NAME=$(basename $@) PART=${PART} $(XRAY_VIVADO) -mode batch -source ../../syn+par.tcl -nojournal -log ../$@.log
	rm -rf *.backup.log

%.fasm: %.bit
	$(XRAY_BIT2FASM) $(BIT2FASM_ARGS) $< > $@
	@sort -u -o $@ $@

%.csv: %.fasm
	python3 ./analyze.py --fasm $< --design $(basename $@).json -o $@

analysis: features.csv unknown_bits.jl

features.csv: $(CSV_FILES) designs.ok
	@head -n 1 $(word 1,$(CSV_FILES)) >features.csv
	@rm -rf features.csv.tmp
	@for f in $(CSV_FILES); \
	do \
	tail -n +2 $$f >>features.csv.tmp; \
	done
	@sort features.csv.tmp >>features.csv
	@rm -rf features.csv.tmp

unknown_bits.jl: $(FASM_FILES) designs.ok
	@cat $(FASM_FILES) | grep unknown_bit | cut -d: -f 2 | sort -u >unknown_bits.jl

snippets: features.csv
	mkdir -p snippets
	cd snippets && python3 ../snippets.py ../$<
