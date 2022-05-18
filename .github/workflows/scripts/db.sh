#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -e

source $(dirname "$0")/hostinfo.sh

echo
echo "======================================="
echo "Creating Vivado Symbolic Link"
echo "---------------------------------------"
ls /opt/Xilinx/Vivado
source /opt/Xilinx/Vivado/2017.2/settings64.sh
vivado -version

echo
echo "========================================"
echo "Downloading current database"
echo "----------------------------------------"
(
	script --return --flush --command "./download-latest-db.sh" -
)
echo "----------------------------------------"

echo
echo "========================================"
echo "Preparing database"
echo "----------------------------------------"
(
	make db-prepare-${XRAY_SETTINGS}
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
	# Output which fuzzers we are going to run
	echo "make --dry-run"
	make --dry-run db-${XRAY_SETTINGS}-all
	echo "----------------------------------------"

	# Run the fuzzers
	set -x +e
	tmp=$(mktemp)
	script --return --flush --command "make -j $CORES MAX_VIVADO_PROCESS=$MAX_VIVADO_PROCESS db-${XRAY_SETTINGS}-all" $tmp
	DATABASE_RET=$?
	set +x -e

	if [[ $DATABASE_RET != 0 ]] ; then
		# Collect the Vivado logs into one tgz archive
		echo "Packing failing test cases"
		# Looking for the failing directories and packing them
		# example of line from which the failing fuzzer directory gets extracted:
		#   - Makefile:87: recipe for target '000-db-init/000-init-db/run.xc7a100tfgg676-1.ok' failed --> fuzzers/000-db-init
		grep -Po "recipe for target '\K(.*)(?=\/run.*\.ok')" $tmp | sed -e 's/^/fuzzers\//' | xargs tar -zcf fuzzers/fails.tgz
		echo "----------------------------------------"
		echo "A failure occurred during Database build."
		echo "----------------------------------------"
		rm $tmp

		echo "========================================"
		echo " Disk space in failure path"
		echo "----------------------------------------"
		du -sh

		exit $DATABASE_RET
	fi
)
echo "----------------------------------------"

# Format the database
make db-format-${XRAY_SETTINGS}
# Update the database/Info.md file
make db-info

# Output if the database has differences
echo
echo "========================================"
echo " Database Differences"
echo "----------------------------------------"
(
	cd database
	# Update the index with any new files
	git add \
		--verbose \
		--all \
		--ignore-errors \
		.

	# Output what git status
	echo
	echo "----------------------------------------"
	echo " Database Status"
	echo "----------------------------------------"
	git status
	echo "----------------------------------------"


	# Output a summary of how the files have changed
	echo
	echo "----------------------------------------"
	echo " Database Diff Summary"
	echo "----------------------------------------"
	git diff --stat --irreversible-delete --find-renames --find-copies --ignore-all-space origin/master

	# Save the diff to be uploaded as an artifact
	echo
	echo "----------------------------------------"
	echo " Saving diff output"
	echo "----------------------------------------"
	# Patch file
	git diff \
		--patch-with-stat --no-color --irreversible-delete --find-renames --find-copies origin/master \
		> diff.patch

	MAX_DIFF_LINES=50000
	DIFF_LINES="$(wc -l diff.patch | sed -e's/ .*$//')"
	if [ $DIFF_LINES -gt $MAX_DIFF_LINES ]; then
		echo
		echo "----------------------------------------"
		echo " Database Diff"
		echo "----------------------------------------"
		echo "diff has $DIFF_LINES lines which is too large to display!"

		echo
		echo "----------------------------------------"
		echo " Generating pretty diff output"
		echo "----------------------------------------"
		echo "diff has $DIFF_LINES lines which is too large for HTML output!"
	else
		# Output the actually diff
		echo
		echo "----------------------------------------"
		echo " Database Diff"
		echo "----------------------------------------"
		git diff --color --irreversible-delete --find-renames --find-copies --ignore-all-space origin/master

		echo
		echo "----------------------------------------"
		echo " Generating pretty diff output"
		echo "----------------------------------------"
		(
			# Allow the diff2html to fail.
			set +e

			# Pretty HTML file version
			diff2html --summary=open --file diff.html --format html \
				-- \
				--irreversible-delete --find-renames --find-copies \
				--ignore-all-space origin/master || true

			# Programmatic JSON version
			diff2html --file diff.json --format json \
				-- \
				--irreversible-delete --find-renames --find-copies \
				--ignore-all-space origin/master || true
		) || true
	fi
)
echo "----------------------------------------"

# Check the database and fail if it is broken.
set -x +e
make db-check-${XRAY_SETTINGS}
CHECK_RET=$?
set +x -e

echo
echo "========================================"
echo " Testing HTML generation"
echo "----------------------------------------"
(
	cd htmlgen
	source htmlgen.sh $XRAY_SETTINGS
)

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
	make clean_fuzzers
	make clean_piplists
)
echo "----------------------------------------"

echo "========================================"
echo " Final disk space after cleanup"
echo "----------------------------------------"
du -sh

exit $CHECK_RET
