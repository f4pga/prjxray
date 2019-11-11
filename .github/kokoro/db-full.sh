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
	script --return --flush --command "./download-latest-db.sh" -
)
echo "----------------------------------------"

source settings/$XRAY_SETTINGS.sh

echo "XRAY_VIVADO_SETTINGS: $XRAY_VIVADO_SETTINGS"
mount
ls -l $XRAY_VIVADO_SETTINGS

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
	#
	# Cap MAX_VIVADO_PROCESS at 20 to limit memory usage of 074 fuzzer.
	# At MAX_VIVADO_PROCESS=20:
	# - 072 completes in ~35 minutes
	# - 074 completes in ~60 minutes
	# which is well before the 05x INT fuzzers complete.
	export MAX_VIVADO_PROCESS=$((CORES/2 < 20 ? CORES/2 : 20))
	set -x +e
	tmp=`mktemp`
	script --return --flush --command "make -j $CORES MAX_VIVADO_PROCESS=$MAX_VIVADO_PROCESS" $tmp
	DATABASE_RET=$?
	set +x -e

	if [[ $DATABASE_RET != 0 ]] ; then
		# Collect the Vivado logs into one tgz archive
		echo "Packing failing test cases"
		grep "recipe for target" $tmp | awk 'match($0,/recipe for target.*'\''(.*)\/run.ok'\''/,res) {print res[1]}' | xargs tar -zcf fails.tgz
		echo "----------------------------------------"
		echo "A failure occurred during Database build."
		echo "----------------------------------------"
		rm $tmp
		exit $DATABASE_RET
	fi

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
# Generate extra files (additional part yaml's, harness, etc).
set +e
# Attempt to generate extras here, but don't check until after diff reporting.
make db-extras-${XRAY_SETTINGS}
EXTRAS_RET=$?
set -e
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

	# Output the actually diff
	echo
	echo "----------------------------------------"
	echo " Database Diff"
	echo "----------------------------------------"
	git diff --color --irreversible-delete --find-renames --find-copies --ignore-all-space origin/master

	# Save the diff to be uploaded as an artifact
	echo
	echo "----------------------------------------"
	echo " Saving diff output"
	echo "----------------------------------------"
	# Patch file
	git diff \
		--patch-with-stat --no-color --irreversible-delete --find-renames --find-copies origin/master \
		> diff.patch

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
)
echo "----------------------------------------"

# Check the database and fail if it is broken.
make db-check-${XRAY_SETTINGS}
if [[ $EXTRAS_RET != 0 ]] ; then
    echo "A failure occurred during extras generation."
    exit $EXTRAS_RET
fi

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
