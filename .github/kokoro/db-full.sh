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

	# Output which fuzzers we are going to run
	echo "make --dry-run"
	make --dry-run
	echo "----------------------------------------"

	# Run the fuzzers
	export MAX_VIVADO_PROCESS=$CORES
	set -x
	script --return --flush --command "make -j $CORES MAX_VIVADO_PROCESS=$CORES" -
	set +x
	echo "----------------------------------------"

	# Check there is nothing to do after running...
	echo
	if [ $(make --dry-run | grep -v 'Nothing to be done' | wc -l) -gt 0 ]; then
		echo "The following targets need to still run!"
		make --dry-run
		echo "----------------------------------------"
		echo "Debug output on why they still need to run"
		make --dry-run --debug
		echo "----------------------------------------"
		exit 1
	else
		echo "All good, nothing more to do!"
	fi
)
echo "----------------------------------------"

# Check the database
#make checkdb-${XRAY_SETTINGS} || true
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
#make checkdb-${XRAY_SETTINGS}

# If we get here, then all the fuzzers completed fine. Hence we are
# going to assume we don't want to keep all the build / logs / etc (as
# they are quite large). Thus do a clean to get rid of them.
echo
echo "========================================"
echo " Cleaning up after success"
echo "----------------------------------------"
(
	cd fuzzers
	echo
	echo "Cleaning up so CI doesn't save all the excess data."
	make clean
)
echo "----------------------------------------"
