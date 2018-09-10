#!/bin/bash

set -ex

source ${XRAY_GENHEADER}

python ../placelut_ff_fb.py --sdx 4 --sdy 4  >placelut.v
vivado -mode batch -source ../generate.tcl

