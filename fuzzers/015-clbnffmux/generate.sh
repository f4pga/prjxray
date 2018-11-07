#!/bin/bash

set -ex
if [ $(vivado -h |grep Vivado |cut -d\  -f 2) != "v2017.2" ] ; then echo "FIXME: requires Vivado 2017.2. See https://github.com/SymbiFlow/prjxray/issues/14"; exit 1; fi
source ${XRAY_DIR}/utils/top_generate.sh

