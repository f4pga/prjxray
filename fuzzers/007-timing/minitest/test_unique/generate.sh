#!/bin/bash

set -ex

source ${XRAY_GENHEADER}
TIMFUZ_DIR=$XRAY_DIR/fuzzers/007-timing

${XRAY_VIVADO} -mode batch -source ../generate.tcl

