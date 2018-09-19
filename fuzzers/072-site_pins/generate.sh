#!/bin/bash -x

source ${XRAY_GENHEADER}

vivado -mode batch -source ../generate.tcl

for f in site_pins_*; do
  python -mjson5.tool --json $f | python -mjson.tool > ${f%.json5}.json
done
