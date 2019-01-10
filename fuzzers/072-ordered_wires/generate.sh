#!/bin/bash -x

source ${XRAY_GENHEADER}

python3 $FUZDIR/run_fuzzer.py

