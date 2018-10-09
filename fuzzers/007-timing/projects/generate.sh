#!/bin/bash

source ${XRAY_GENHEADER}
TIMFUZ_DIR=$XRAY_DIR/fuzzers/007-timing

timing_txt2csv () {
    python3 $TIMFUZ_DIR/timing_txt2icsv.py --speed-json $TIMFUZ_DIR/speed/build/speed.json --out timing4i.csv.tmp timing4.txt
    mv timing4i.csv.tmp timing4i.csv

    python3 $TIMFUZ_DIR/timing_txt2scsv.py --speed-json $TIMFUZ_DIR/speed/build/speed.json --out timing4s.csv.tmp timing4.txt
    mv timing4s.csv.tmp timing4s.csv

    # delete really large file, see https://github.com/SymbiFlow/prjxray/issues/137
    rm timing4.txt
}

