#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -e

echo '::group::Host Environment'
export
echo '::endgroup::'

echo '::group::Host CPU'
export CORES=$(nproc --all)
echo "Cores: $CORES"
echo
echo "Memory"
echo "----------------------------------------"
cat /proc/meminfo
echo "----------------------------------------"
export MEM_GB=$(($(awk '/MemTotal/ {print $2}' /proc/meminfo)/(1024*1024)))
echo "Total Memory (GB): $MEM_GB"
echo '::endgroup::'

# Approx memory per grid process
export MEM_PER_RUN=8
export MAX_GRID_CPU=$(($MEM_GB/$MEM_PER_RUN))
export MAX_VIVADO_PROCESS=$(($MEM_GB/$MEM_PER_RUN))

echo '::group::Source Vivado settings'
ls /opt/Xilinx/Vivado
source /opt/Xilinx/Vivado/2017.2/settings64.sh
vivado -version
echo '::endgroup::'

echo '::group::Downloading current database'
script --return --flush --command "./download-latest-db.sh" -
echo '::endgroup::'

echo '::group::Preparing database'
make db-prepare-${XRAY_SETTINGS}
echo '::endgroup::'

source settings/$XRAY_SETTINGS.sh

echo '::group::Cleaning out current database'
(
	cd database
	make clean-${XRAY_SETTINGS}-db
)
echo '::endgroup::'

echo '::group::Running Database build'
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
echo '::endgroup::'

# Format the database
make db-format-${XRAY_SETTINGS}
# Update the database/Info.md file
make db-info

# Output if the database has differences
echo '::group::Database Differences'
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
	echo " Database Status"
	echo "----------------------------------------"
	git status
	echo "----------------------------------------"


	# Output a summary of how the files have changed
	echo
	echo " Database Diff Summary"
	echo "----------------------------------------"
	git diff --stat --irreversible-delete --find-renames --find-copies --ignore-all-space origin/master

	# Save the diff to be uploaded as an artifact
	echo
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
		echo " Database Diff"
		echo "----------------------------------------"
		echo "diff has $DIFF_LINES lines which is too large to display!"

		echo
		echo " Generating pretty diff output"
		echo "----------------------------------------"
		echo "diff has $DIFF_LINES lines which is too large for HTML output!"
	else
		# Output the actually diff
		echo
		echo " Database Diff"
		echo "----------------------------------------"
		git diff --color --irreversible-delete --find-renames --find-copies --ignore-all-space origin/master

		echo
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
echo '::endgroup::'

# Check the database and fail if it is broken.
set -x +e
make db-check-${XRAY_SETTINGS}
CHECK_RET=$?
set +x -e

echo '::group::Testing HTML generation'
(
	cd htmlgen
	source htmlgen.sh $XRAY_SETTINGS
)
echo '::endgroup::'

# If we get here, then all the fuzzers completed fine. Hence we are
# going to assume we don't want to keep all the build / logs / etc (as
# they are quite large). Thus do a clean to get rid of them.
echo '::group::Cleaning up after success'
(
	cd fuzzers
	echo
	echo "Cleaning up so CI doesn't save all the excess data."
	make clean_fuzzers
	make clean_piplists
)
echo '::endgroup::'

echo '::group::Final disk space after cleanup'
du -sh
echo '::endgroup::'

exit $CHECK_RET
