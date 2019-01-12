#!/bin/bash

set -x
set -e

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

echo "----------------------------------------"
echo "----------------------------------------"
echo "----------------------------------------"

export

echo "----------------------------------------"
echo "----------------------------------------"
echo "----------------------------------------"

find .

echo "----------------------------------------"
echo "----------------------------------------"
echo "----------------------------------------"

echo $PWD

echo "----------------------------------------"

cd github/$KOKORO_DIR/

git fetch --tags || true
git describe --tags || true

# Build the C++ tools
make build --output-sync=target --warn-undefined-variables

# Setup the Python environment
make env --output-sync=target --warn-undefined-variables

echo "----------------------------------------"
echo "----------------------------------------"
echo "----------------------------------------"

find .

echo "----------------------------------------"
echo "----------------------------------------"
echo "----------------------------------------"

# Run the tests
make test --output-sync=target --warn-undefined-variables

echo "----------------------------------------"
echo "----------------------------------------"
echo "----------------------------------------"

cat build/*test_results.xml
mkdir build/py
cp build/py_test_results.xml build/py/sponge_log.xml
mkdir build/cpp
cp build/cpp_test_results.xml build/cpp/sponge_log.xml

echo "----------------------------------------"
echo "----------------------------------------"
echo "----------------------------------------"
