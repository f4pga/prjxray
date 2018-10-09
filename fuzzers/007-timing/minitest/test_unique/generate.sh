#!/bin/bash

set -ex

source ${XRAY_GENHEADER}
TIMFUZ_DIR=$XRAY_DIR/fuzzers/007-timing

vivado -mode batch -source ../generate.tcl

