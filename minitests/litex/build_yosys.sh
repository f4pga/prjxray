#!/bin/bash
set -e
cd yosys
make config-gcc
make -j`nproc`
