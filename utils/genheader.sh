# header for fuzzer generate.sh scripts
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

if [ -z "$XRAY_DATABASE" ]; then
	echo "No XRAY environment found. Make sure to source the settings file first!"
	exit 1
fi

set -ex

export FUZDIR=$PWD

# for some reason on sourced script set -e doesn't work
# Scripts may have additional arguments, but first is reserved for build directory
test $# -ge 1 || exit 1
test ! -e "$SPECDIR"
export SPECDIR=$1

mkdir -p "$SPECDIR"
cd "$SPECDIR"

export SEED="$(echo $SPECDIR | md5sum | cut -c1-8)"
export SEEDN="$(basename $(pwd) |sed s/specimen_0*//)"

function seed_vh () {
    echo '`define SEED 32'"'h${SEED}" > setseed.vh
}

