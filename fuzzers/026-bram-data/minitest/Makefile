# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# WARNING: probably don't do more than -j 2
# diff.mk can overlap in a few cases

all:  build/env build/roi_bram18d_bit01.diff build/roi_bram36d_bit01.diff build/roi_bramd_bits01.diff build/roi_bramds_bit01.diff

clean:
	rm -rf build

# hard coded LOCs in .v
build/env:
	test "$(XRAY_PART)" = "xc7a50tfgg484-1"

# Toggle one bit to locate where first BRAM data is (BRAM18)
build/roi_bram18d_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bram18d_bit01.diff PRJL=roi_bram18d_bit0 PRJR=roi_bram18d_bit1

# Toggle one bit to locate where first BRAM data is (BRAM36)
build/roi_bram36d_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bram36d_bit01.diff PRJL=roi_bram36d_bit0 PRJR=roi_bram36d_bit1

# Toggle all bits in a single BRAM data section
build/roi_bramd_bits01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bramd_bits01.diff PRJL=roi_bramd_bits0 PRJR=roi_bramd_bits1

# Toggle one bit in each BRAM data section
build/roi_bramds_bit01.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_bramds_bit01.diff PRJL=roi_bramds_bit0 PRJR=roi_bramds_bit1


