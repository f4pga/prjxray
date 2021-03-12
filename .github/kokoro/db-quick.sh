#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -e

cd github/$KOKORO_DIR/

source ./.github/kokoro/steps/hostcheck.sh
source ./.github/kokoro/steps/hostsetup.sh
source ./.github/kokoro/steps/hostinfo.sh
source ./.github/kokoro/steps/git.sh

source ./.github/kokoro/steps/xilinx.sh

source ./.github/kokoro/steps/prjxray-env.sh

echo
echo "========================================"
echo "Downloading current database"
echo "----------------------------------------"
(
	./download-latest-db.sh
)
echo "----------------------------------------"

source settings/$XRAY_SETTINGS.sh

echo
echo "========================================"
echo "Running quick fuzzer sanity check"
echo "----------------------------------------"
(
	cd fuzzers
	echo "make --dry-run"
	make --dry-run
	echo "----------------------------------------"
	export MAX_VIVADO_PROCESS=$CORES
	set -x
	script --return --flush --command "make -j $CORES MAX_VIVADO_PROCESS=$CORES QUICK=y" -
	set +x
)
echo "----------------------------------------"
