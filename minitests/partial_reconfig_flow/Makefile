# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
.PRECIOUS: harness_impl.dcp %_impl.dcp %.bit %_roi_partial.bit

# Top-level target for generating a programmable bitstream.  Given a .fasm
# file, calling make with the .fasm extension replaced with _hand_crafted.bit
# will generate a bitstream that includes both the harness and the .fasm design
# ready for programming to a board.  For example,
# 'make inv_hand_crafted.bit' will generate a bitstream that includes the
# design from roi_noninv.fasm.
%_hand_crafted.bit: %_roi_partial.frm harness.bit
	${XRAY_TOOLS_DIR}/xc7patch \
		--part_name "${XRAY_PART}" \
		--part_file "${XRAY_PART_YAML}" \
		--bitstream_file harness.bit \
		--frm_file $< \
		--output_file $@

# Generate a suitable harness by using Vivado's partial reconfiguration
# feature.  inv.v is used as a sample reconfiguration design as one is
# required to generate a partial reconfiguration design.
harness_synth.dcp: harness_synthesize.tcl harness.v
	${XRAY_VIVADO} -mode batch -source harness_synthesize.tcl

harness_impl.dcp: harness_synth.dcp inv_synth.dcp harness_implement.tcl
	${XRAY_VIVADO} -mode batch -source harness_implement.tcl

# Synthesize an ROI design
%_synth.dcp: %.v roi_synthesize.tcl
	${XRAY_VIVADO} -mode batch -source roi_synthesize.tcl -tclargs $< $@

# Implement an ROI design
%_impl.dcp: %_synth.dcp harness_impl.dcp roi_implement.tcl
	${XRAY_VIVADO} -mode batch -source roi_implement.tcl -tclargs $< $@

# Generate bitstreams from an implemented design.  Two bitstreams are
# generated: one containing a complete design including the harness (.bit) and
# one that only contains the frames that implement the ROI design
# (_roi_partial.bit).
%.bit: %_impl.dcp write_bitstream.tcl
	${XRAY_VIVADO} -mode batch -source write_bitstream.tcl -tclargs $< $@
%_roi_partial.bit: %.bit ;

# Conversions between various formats.
%.bits: %.bit
	${XRAY_BITREAD} -z -y -o $@ $<

%.segp: %.bits
	${XRAY_SEGPRINT} -zd $< > $@

%.fasm: %.segp
	${XRAY_DIR}/tools/segprint2fasm.py $< $@

%.frm: %.fasm
	${XRAY_DIR}/tools/fasm2frame.py $< $@

# This format is a human-readable representation of the configuration packets
# used to interact with 7-series chips over JTAG.
%.packets: %.bit
	${XRAY_TOOLS_DIR}/bittool list_config_packets $< > $@

clean:
	rm -rf vivado*.log vivado_*.str vivado*.jou design *.bits *.dcp *.bit design.txt .Xil
	rm -rf *.frm *.segp *.packets *.bin *.fasm
	rm -rf hd_visual

.PHONY: clean

