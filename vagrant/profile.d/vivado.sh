#!/bin/sh

VIVADO_BIN="$(find /opt/Xilinx/Vivado -maxdepth 2 -name bin)"
if [ -n "$VIVADO_BIN" ]; then
	export PATH=$PATH:$VIVADO_BIN
fi
