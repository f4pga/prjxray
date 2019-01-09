#!/bin/bash

set -e
set -x

sudo apt-get update
sudo apt-get install -y \
        bison \
        build-essential \
        ca-certificates \
        clang-format \
        cmake \
        curl \
        flex \
        fontconfig \
        git \
        jq \
        python \
        python3 \
        python3-dev \
        python3-virtualenv \
        python3-yaml \
        virtualenv \

ls -l ~/.Xilinx
sudo chown -R $USER ~/.Xilinx

cd github/symbiflow-prjxray-artix7/

git fetch --tags || true
git describe --tags || true

# Build the C++ tools
make build --output-sync=target --warn-undefined-variables

# Setup the Python environment
make env --output-sync=target --warn-undefined-variables

source settings/artix7.sh
(
	export XILINX_LOCAL_USER_DATA=no
	cd fuzzers
	make --output-sync=target --warn-undefined-variables QUICK=y
)
