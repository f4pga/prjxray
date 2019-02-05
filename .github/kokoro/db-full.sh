#!/bin/bash

set -e

cd github/$KOKORO_DIR/

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
echo "Cleaning out current database"
echo "----------------------------------------"
(
	cd database
	make clean-${XRAY_SETTINGS}-db
)
echo "----------------------------------------"

echo
echo "========================================"
echo "Running Database build"
echo "----------------------------------------"
(
	cd fuzzers
	echo "make --dry-run"
	make --dry-run
	echo "----------------------------------------"
	export MAX_VIVADO_PROCESS=$CORES
	set -x
	script --return --flush --command "make -j $CORES MAX_VIVADO_PROCESS=$CORES" -
	set +x
	echo "----------------------------------------"
	echo "make --dry-run"
	make --dry-run
)
echo "----------------------------------------"

# Check the database
make checkdb-${XRAY_SETTINGS} || true
# Format the database
make formatdb-${XRAY_SETTINGS}

# Output if the database has differences
echo
echo "========================================"
echo " Database Differences"
echo "----------------------------------------"
(
	cd database
	echo "----------------------------------------"
	echo " Database Status"
	echo "----------------------------------------"
	git status
	echo "----------------------------------------"
	echo
	echo
	echo
	echo "----------------------------------------"
	echo " Database Diff"
	echo "----------------------------------------"
	git diff
)
echo "----------------------------------------"

# Check the database and fail if it is broken.
make checkdb-${XRAY_SETTINGS}
