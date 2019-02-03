#!/bin/bash

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
