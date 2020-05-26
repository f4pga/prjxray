# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
all:

clean:
	rm -r build

build/.touch:
	mkdir -p build
	touch build/.touch

%.json: %.json5
	python3 ${XRAY_UTILS_DIR}/clean_json5.py < $< > $@

CURDIR=$(shell pwd)

define output_timing

# $(1) - ITER
# $(2) - DESIGN_NAME
# $(3) - VERILOGS

build/$(2)_$(1)/timing_$(2)_$(1).json5: build/.touch runme.tcl ${XRAY_UTILS_DIR}/write_timing_info.tcl $(3)
	rm -rf build/$(2)_$(1)
	mkdir -p build/$(2)_$(1)
	export ITER=$(1) DESIGN_NAME=$(2) VERILOGS="$(3)" && cd build/$(2)_$(1) && \
		 ${XRAY_VIVADO} -mode batch -source ${CURDIR}/runme.tcl > design_$(2)_$(1)_vivado.log

build/timing_$(2)_$(1).xlsx: build/$(2)_$(1)/timing_$(2)_$(1).json ${XRAY_UTILS_DIR}/create_timing_worksheet_db.py
	python3 ${XRAY_UTILS_DIR}/create_timing_worksheet_db.py \
		--timing_json build/$(2)_$(1)/timing_$(2)_$(1).json \
		--db_root ${XRAY_FAMILY_DIR} \
		--part ${XRAY_PART} \
		--output_xlsx build/timing_$(2)_$(1).xlsx

build/$(2)_$(1)/design_$(2)_$(1).fasm: build/$(2)_$(1)/timing_$(2)_$(1).json
	${XRAY_BIT2FASM} --verbose build/$(2)_$(1)/design_$(2)_$(1).bit > build/$(2)_$(1)/design_$(2)_$(1).fasm

$(2)_$(1): build/timing_$(2)_$(1).xlsx build/$(2)_$(1)/design_$(2)_$(1).fasm

$(2): $(2)_$(1)

.PHONY: $(2) $(2)_$(1)

all: $(2)_$(1)

endef

$(foreach ITER,$(shell seq 1 63), $(eval $(call output_timing,$(ITER),dff,${CURDIR}/top_dff.v)))
$(foreach ITER,$(shell seq 1 63), $(eval $(call output_timing,$(ITER),cff,${CURDIR}/top_cff.v)))
$(foreach ITER,$(shell seq 1 63), $(eval $(call output_timing,$(ITER),bff,${CURDIR}/top_bff.v)))
$(foreach ITER,$(shell seq 1 63), $(eval $(call output_timing,$(ITER),aff,${CURDIR}/top_aff.v)))
$(foreach ITER,$(shell seq 1 63), $(eval $(call output_timing,$(ITER),dff2,${CURDIR}/top_dff2.v)))
$(foreach ITER,$(shell seq 1 63), $(eval $(call output_timing,$(ITER),dff_inter,${CURDIR}/top_dff_inter.v)))
$(foreach ITER,$(shell seq 1 63), $(eval $(call output_timing,$(ITER),dff_slicem,${CURDIR}/top_dff_slicem.v)))
$(foreach ITER,20 50 100 1000 10000, $(eval $(call output_timing,$(ITER),fanout,${CURDIR}/top_fanout.v)))
$(foreach ITER,0, $(eval $(call output_timing,$(ITER),fanout_ex,${CURDIR}/fanout_ex.v)))
$(foreach ITER,0, $(eval $(call output_timing,$(ITER),counter,${CURDIR}/top_counter.v)))
$(foreach ITER,$(shell seq 1 3), $(eval $(call output_timing,$(ITER),picorv32, \
	$(addprefix ${CURDIR}/, \
		picosoc_noflash.v picorv32.v progmem.v basys3_demo.v simpleuart.v))))

.PHONY: all clean
