#!/bin/bash

set -ex
source ../generate.sh

python ../generate.py --sdx 4 --sdy 4  >top.v
vivado -mode batch -source ../generate.tcl
timing_txt2csv

