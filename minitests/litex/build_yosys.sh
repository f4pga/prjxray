#!/bin/bash
set -e
cd ../../third_party/yosys
make config-gcc
make -j`nproc`
