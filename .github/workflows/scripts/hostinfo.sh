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
echo "Host Environment"
echo "----------------------------------------"
export
echo "----------------------------------------"

echo
echo "========================================"
echo "Host CPU"
echo "----------------------------------------"
export CORES=$(nproc --all)
echo "Cores: $CORES"
echo
echo "Memory"
echo "----------------------------------------"
cat /proc/meminfo
echo "----------------------------------------"
export MEM_GB=$(($(awk '/MemTotal/ {print $2}' /proc/meminfo)/(1024*1024)))
echo "Total Memory (GB): $MEM_GB"

# Approx memory per grid process
export MEM_PER_RUN=8
export MAX_GRID_CPU=$(($MEM_GB/$MEM_PER_RUN))
export MAX_VIVADO_PROCESS=$(($MEM_GB/$MEM_PER_RUN))

echo
echo "========================================"
echo "Host files"
echo "----------------------------------------"
echo $PWD
echo "----------------------------------------"
find . | sort
echo "----------------------------------------"
