# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# WARNING: probably don't do more than -j 2
# diff.mk can overlap in a few cases

all:  build/env build/roi_brami_bit01.diff build/roi_bramis_bit01.diff build/roi_bram18_width.diff build/roi_bram18_write_mode.diff build/roi_bram18_ram_mode.diff

clean:
	rm -rf build

# hard coded LOCs in .v
build/env:
	test "$(XRAY_PART)" = "xc7a50tfgg484-1"

# Toggle one bit in BRAM config section
build/roi_brami_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_brami_bit01.diff PRJL=roi_brami_bit0 PRJR=roi_brami_bit1

# Toggle one bit in each BRAM config section
build/roi_bramis_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bramis_bit01.diff PRJL=roi_bramis_bit0 PRJR=roi_bramis_bit1

build/roi_bram18_width.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bram18_width.diff PRJL=roi_bram18_width_a PRJR=roi_bram18_width_b

build/roi_bram18_write_mode.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bram18_write_mode.diff PRJL=roi_bram18_write_mode_a PRJR=roi_bram18_write_mode_b

build/roi_bram18_ram_mode.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bram18_ram_mode.diff PRJL=roi_bram18_ram_mode_tdp PRJR=roi_bram18_ram_mode_sdp

