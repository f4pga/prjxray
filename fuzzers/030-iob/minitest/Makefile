# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
all:  build/env build/roi_roi_io.diff \
    build/PULLTYPE/run.ok \
    build/SLEW/run.ok \
    build/DRIVE/run.ok \
    build/IOSTANDARD/run.ok \

clean:
	rm -rf build

# hard coded LOCs in .v
build/env:
	test "$(XRAY_PART)" = "xc7a50tfgg484-1"

# Didn't work
build/roi_io.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_io.diff PRJL=roi_io_a PRJR=roi_io_b

# Didn't work
build/roi_prop.diff:
	$(MAKE) -f diff.mk OUT_DIFF=build/roi_prop.diff PRJL=roi_prop_a PRJR=roi_prop_b

build/PULLTYPE/run.ok:
	PROJECT=PULLTYPE bash runme_tcl.sh
	diff build/PULLTYPE/design_{PULLDOWN,KEEPER}.bits || true
	diff build/PULLTYPE/design_{PULLDOWN,PULLUP}.bits || true
	diff build/PULLTYPE/design_{PULLDOWN,NONE}.bits || true

build/SLEW/run.ok:
	PROJECT=SLEW bash runme_tcl.sh

build/DRIVE/run.ok:
	PROJECT=DRIVE bash runme_tcl.sh

build/IOSTANDARD/run.ok:
	PROJECT=IOSTANDARD bash runme_tcl.sh

csv:
	PROJECT=$@ bash runme.sh

