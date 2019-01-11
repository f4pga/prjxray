#!/bin/bash -x

source ${XRAY_GENHEADER}

${XRAY_VIVADO} -mode batch -source $FUZDIR/generate.tcl

cd .. && ./generate_after_dump.sh
