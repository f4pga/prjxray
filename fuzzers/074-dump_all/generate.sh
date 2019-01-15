#!/bin/bash -x

source ${XRAY_GENHEADER}

python3 $FUZDIR/run_fuzzer.py $2 $3 $4

cd $FUZDIR && ./generate_after_dump.sh
