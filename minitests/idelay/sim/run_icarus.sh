#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -e

# Check args
if [ "$#" -ne 1 ]; then
    echo "Usage: run_vivado.sh <testbench file>"
    exit -1
fi

# Check if testbench exists
if [ ! -f $1 ]; then
    echo "Testbench $1 not found!"
    exit -1
fi

# Compile
iverilog -v -g2005 -s tb -o testbench.vvp $1

# Run
vvp -v testbench.vvp

