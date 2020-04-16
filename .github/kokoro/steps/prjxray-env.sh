#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -e

echo
echo "========================================"
echo "Build the C++ tools"
echo "----------------------------------------"
make build --output-sync=target --warn-undefined-variables -j $CORES
echo "----------------------------------------"

echo
echo "========================================"
echo "Setup the Python environment"
echo "----------------------------------------"
make env --output-sync=target --warn-undefined-variables
