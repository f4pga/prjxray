#!/bin/bash

set -ex

FUZDIR=$PWD
source ${XRAY_GENHEADER}

echo '`define SEED 32'"'h$(echo $1 | md5sum | cut -c1-8)" > setseed.vh

vivado -mode batch -source $FUZDIR/generate.tcl

${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
python3 $FUZDIR/generate.py

