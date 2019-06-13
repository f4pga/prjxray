#!/bin/bash
set -e
export DEFCONFIG=`realpath ./configs/ct.config`
cd ../../third_party/crosstool-ng
./bootstrap
./configure --enable-local
make -j`nproc`
./ct-ng defconfig
./ct-ng build.`nproc`
touch build.ok
