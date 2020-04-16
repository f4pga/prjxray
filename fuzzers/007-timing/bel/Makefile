# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
SLICEL_SDFS = build/CLBLL_L.sdf build/CLBLL_R.sdf build/CLBLM_L.sdf build/CLBLM_R.sdf
SLICEM_SDFS = build/CLBLL_L.sdf build/CLBLL_R.sdf build/CLBLM_L.sdf build/CLBLM_R.sdf

all: build/all_sdf.ok

build/all_sdf.ok: build/carry4_slicel.sdf build/carry4_slicem.sdf
	touch build/all_sdf.ok
clean:
	rm -rf build

build/run.ok:
	bash runme.sh
	touch build/run.ok

build/fixup_timings: build/run.ok
	python3 fixup_timings_txt.py --txtin build/bel_timings.txt --txtout build/bel_timings.txt --site RAMBFIFO36E1 --slice BRAM_L --type timings
	python3 fixup_timings_txt.py --txtin build/bel_timings.txt --txtout build/bel_timings.txt --site RAMBFIFO36E1 --slice BRAM_R --type timings
	python3 fixup_timings_txt.py --txtin build/bel_pins.txt --txtout build/bel_pins.txt --site RAMBFIFO36E1 --slice BRAM_L --type pins
	python3 fixup_timings_txt.py --txtin build/bel_pins.txt --txtout build/bel_pins.txt --site RAMBFIFO36E1 --slice BRAM_R --type pins
	python3 fixup_timings_txt.py --txtin build/bel_properties.txt --txtout build/bel_properties.txt --site RAMBFIFO36E1 --slice BRAM_L --type properties
	python3 fixup_timings_txt.py --txtin build/bel_properties.txt --txtout build/bel_properties.txt --site RAMBFIFO36E1 --slice BRAM_R --type properties
	touch build/fixup_timings

build/bel_timings.json: build/fixup_timings
	python3 tim2json.py --timings=build/bel_timings.txt --json=build/bel_timings.json --properties=build/bel_properties.txt --propertiesmap=properties_map.json --pinaliasmap=pin_alias_map.json --belpins=build/bel_pins.txt --sitepins=build/tile_pins.txt --debug true

build/sdf.ok: build/bel_timings.json
	python3 ${XRAY_UTILS_DIR}/makesdf.py --json=${PWD}/build/bel_timings.json --sdf=${PWD}/build
	touch build/sdf.ok

build/slicem.sdf: build/sdf.ok
	python3 ${XRAY_UTILS_DIR}/sdfmerge.py --sdfs $(SLICEL_SDFS) --site SLICEM --out build/slicem.sdf

build/slicel.sdf: build/sdf.ok
	python3 ${XRAY_UTILS_DIR}/sdfmerge.py --sdfs $(SLICEL_SDFS) --site SLICEL --out build/slicel.sdf

build/carry4_slicem.sdf: build/slicem.sdf
	python3 carry4delays.py --input build/slicem.sdf --output build/carry4_slicem.sdf

build/carry4_slicel.sdf: build/slicel.sdf
	python3 carry4delays.py --input build/slicel.sdf --output build/carry4_slicel.sdf
