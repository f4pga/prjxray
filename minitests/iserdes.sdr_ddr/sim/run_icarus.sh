#!/bin/bash

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

# Create sources file
cp sources.cf.template sources.cf
echo $1 >> sources.cf

# Compile
iverilog -v -c sources.cf -g2005 -s tb -o testbench.vvp

# Run
vvp -v testbench.vvp

