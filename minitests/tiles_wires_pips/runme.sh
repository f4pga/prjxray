#!/bin/bash

set -e
vivado -mode batch -source runme.tcl
echo "=========================================================="
md5sum wires_{INT,CLBLL,CLBLM}_[LR]_*.txt | sed -re 's,X[0-9]+Y[0-9]+,XY,' | sort | uniq -c | sort -k3
echo "=========================================================="
md5sum pips_{INT,CLBLL,CLBLM}_[LR]_*.txt | sed -re 's,X[0-9]+Y[0-9]+,XY,' | sort | uniq -c | sort -k3
