#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

function display_help() {
    echo "This is a utility script that helps displaying the total"
    echo "amount of unknown bits in the various minitest."
    echo ""
    echo "The minitest must contain a Makefile which flow ends in the"
    echo "generation of a FASM file."
    echo ""
    echo "Arguments:"
    echo " -m|--minitests: list of minitest directories from which the FASM files are"
    echo "                 generated and parsed to get the total amount of missing"
}

MINITEST_DIRS=()

MINITEST=0

for arg in $@; do
    case "$arg" in
        -m|--minitests)
            MINITEST=1
            ;;
        *)
        if [ $MINITEST -eq 1 ]; then
            MINITEST_DIRS+=($arg)
        else
            display_help
            exit 1
        fi
        ;;
    esac
done

if [ $# -eq 0  ]; then
    display_help
    exit 1
fi

for MINITEST in ${MINITEST_DIRS[*]}
do
    echo "-----------------------------"
    echo "$MINITEST"
    echo "-----------------------------"
    make -q -C $MINITEST all
    FASM_FILE=`find $MINITEST -name "*.fasm"`
    MISSING_BITS=`grep "unknown_bit" $FASM_FILE | wc -l`
    MISSING_FRAMES=`grep "In frame" $FASM_FILE | wc -l`

    echo "Total of unknown bits: $MISSING_BITS"
    echo "Total of unknown frames: $MISSING_FRAMES"
    echo ""
done
