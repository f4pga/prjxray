#!/usr/bin/env bash
# Development script to re-run segment generation on specimens
# Works against most but not all fuzzers

set -ex

FUZDIR=$PWD
pushd build

for f in $(find -name design.bits) ; do
     pushd $(dirname $f)
     python3 $FUZDIR/generate.py
     popd
done
popd

${XRAY_SEGMATCH} -o build/tmp.segbits $(find -name 'segdata_*.txt')
cat build/tmp.segbits

