#!/bin/bash

set -ex
if [ $(vivado -h |grep Vivado |cut -d\  -f 2) != "v2017.2" ] ; then echo "FIXME: requires Vivado 2017.2. See https://github.com/SymbiFlow/prjxray/issues/14"; exit 1; fi

source ${XRAY_GENHEADER}

#echo '`define SEED 32'"'h$(echo $1 | md5sum | cut -c1-8)" > setseed.vh

python3 ../top.py >top.v
vivado -mode batch -source ../generate.tcl
test -z "$(fgrep CRITICAL vivado.log)"

for x in design*.bit; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${x}s -z -y $x
done

python3 ../generate.py

