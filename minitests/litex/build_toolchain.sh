#!/bin/bash

cd ct
./bootstrap
./configure --enable-local
make -j`nproc`
DEFCONFIG=../configs/ct.config ./ct-ng defconfig
./ct-ng build.`nproc`
touch toolchain.ok
