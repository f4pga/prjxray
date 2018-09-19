#!/bin/bash -x

source ${XRAY_GENHEADER}

vivado -mode batch -source ../generate.tcl

for f in site_pins_*; do
  echo "Cleaning up $f"
  python ../cleanup_site_pins.py < $f  > ${f%.json5}.json
done
