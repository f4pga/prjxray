#!/bin/bash

set -ex
source ../generate.sh

python ../generate.py --sdx 4 --sdy 4  >top.v
${XRAY_VIVADO} -mode batch -source ../generate.tcl
timing_txt2csv

