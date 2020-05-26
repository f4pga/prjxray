# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
all: build/slicel.sdf build/slicem.sdf
	touch build/sdf.ok

clean:
	rm -rf build

build/slicel.sdf: build/run.ok
	python3 tim2sdf.py --timings build/slicel.txt --site SLICEL --sdf build/slicel.sdf

build/slicem.sdf: build/run.ok
	python3 tim2sdf.py --timings build/slicem.txt --site SLICEM --sdf build/slicem.sdf

build/run.ok:
	bash runme.sh

cleandb:
	rm -rf ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/timings

