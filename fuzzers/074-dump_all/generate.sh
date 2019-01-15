#!/bin/bash -x

source ${XRAY_GENHEADER}

${XRAY_VIVADO} -mode batch -source $FUZDIR/generate.tcl

cd $FUZDIR && ./generate_after_dump.sh
