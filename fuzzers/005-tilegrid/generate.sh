#!/bin/bash -x

PRJ=$2

export FUZDIR=$PWD
source ${XRAY_GENHEADER}

vivado -mode batch -source $FUZDIR/generate_$PRJ.tcl
test -z "$(fgrep CRITICAL vivado.log)"

if [ $PRJ != "tiles" ] ; then
    for x in design*.bit; do
	    ${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${x}s -z -y $x
    done

    for x in design_*.bits; do
	    diff -u design.bits $x | grep '^[-+]bit' > ${x%.bits}.delta
    done
    touch deltas
fi

