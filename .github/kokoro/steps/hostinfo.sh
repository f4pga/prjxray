#!/bin/bash

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
export MEM_PER_GRID=8
export MAX_CPU_PER_GRID=$(($MEM_GB/$MEM_PER_RUN))

echo
echo "========================================"
echo "Host files"
echo "----------------------------------------"
echo $PWD
echo "----------------------------------------"
find . | sort
echo "----------------------------------------"
