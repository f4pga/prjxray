#!/bin/bash

set -e

cd github/$KOKORO_DIR/

source ./.github/kokoro/steps/hostsetup.sh
source ./.github/kokoro/steps/hostinfo.sh
source ./.github/kokoro/steps/git.sh

source ./.github/kokoro/steps/prjxray-env.sh

echo
echo "========================================"
echo "Running tests"
echo "----------------------------------------"
(
	make test --output-sync=target --warn-undefined-variables
)
echo "----------------------------------------"

echo
echo "========================================"
echo "Copying tests logs"
echo "----------------------------------------"
(
	cat build/*test_results.xml
	mkdir build/py
	cp build/py_test_results.xml build/py/sponge_log.xml
	mkdir build/cpp
	cp build/cpp_test_results.xml build/cpp/sponge_log.xml
)
echo "----------------------------------------"
