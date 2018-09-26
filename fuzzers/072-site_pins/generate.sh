#!/bin/bash -x

source ${XRAY_GENHEADER}

vivado -mode batch -source ../generate.tcl

for f in site_pins_*; do
  echo "Cleaning up $f"
  noext_filename=${f%.json5}
  noprefix_filename=${noext_filename#site_pins_}
  python ../cleanup_site_pins.py $f < $f > ${noext_filename}.json
  python ../generate_tile_wires.py $f < $f > tile_wires_${noprefix_filename}.json
done
