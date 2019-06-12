#!/bin/bash
set -e
cd crosstool-ng
./bootstrap
./configure --enable-local
make -j`nproc`
DEFCONFIG=../configs/ct.config ./ct-ng defconfig
./ct-ng build.`nproc`
touch build.ok
