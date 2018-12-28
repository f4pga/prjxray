#!/bin/bash

source "${XRAY_VIVADO_SETTINGS:-/opt/Xilinx/Vivado/2017.2/settings64.sh}"

vivado "$@"
