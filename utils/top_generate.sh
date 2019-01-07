#!/bin/bash
# Generic generate.sh for scripts that use top.py to generate top.v
# and then use generate.py for segment generation

set -ex

export FUZDIR=$PWD
source ${XRAY_GENHEADER}
make -f $XRAY_DIR/utils/top_generate.mk

