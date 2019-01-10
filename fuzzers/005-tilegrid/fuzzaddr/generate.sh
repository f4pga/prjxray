#!/bin/bash

set -ex

export FUZDIR=$PWD
source ${XRAY_GENHEADER}

# Some projects have hard coded top.v, others are generated
if [ -f $FUZDIR/top.py ] ; then
    XRAY_DATABASE_ROOT=$FUZDIR/../build/basicdb python3 $FUZDIR/top.py >top.v
fi

${XRAY_VIVADO} -mode batch -source $FUZDIR/generate.tcl
test -z "$(fgrep CRITICAL vivado.log)"

for x in design*.bit; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${x}s -z -y $x
done

python3 $GENERATE_PY $GENERATE_ARGS >segdata_tilegrid.txt

