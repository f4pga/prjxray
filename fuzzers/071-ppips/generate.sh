#!/bin/bash -x

source ${XRAY_GENHEADER}

vivado -mode batch -source ../generate.tcl

