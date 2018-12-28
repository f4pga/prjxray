#!/bin/bash

set -ex
source ../generate.sh

${XRAY_VIVADO} -mode batch -source ../generate.tcl
timing_txt2csv

