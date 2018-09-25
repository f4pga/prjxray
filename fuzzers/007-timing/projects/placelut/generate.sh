#!/bin/bash

set -ex

source ${XRAY_GENHEADER}
TIMFUZ_DIR=$XRAY_DIR/fuzzers/007-timing

python ../generate.py --sdx 4 --sdy 4  >top.v
vivado -mode batch -source ../generate.tcl
python3 $TIMFUZ_DIR/timing_txt2csv.py --speed-json $TIMFUZ_DIR/speed/build/speed.json --out timing4.csv timing4.txt

