#!/bin/bash

set -ex
source ../generate.sh

vivado -mode batch -source ../generate.tcl
timing_txt2csv

