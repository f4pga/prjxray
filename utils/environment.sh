# dirs
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
XRAY_ENV_PATH="${BASH_SOURCE[0]}"
while [ -h "$XRAY_ENV_PATH" ]; do # resolve $XRAY_ENV_PATH until the file is no longer a symlink
  XRAY_UTILS_DIR="$( cd -P "$( dirname "$XRAY_ENV_PATH" )" && pwd )"
  XRAY_ENV_PATH="$(readlink "$XRAY_ENV_PATH")"
  [[ $XRAY_ENV_PATH != /* ]] && XRAY_ENV_PATH="$XRAY_UTILS_DIR/$XRAY_ENV_PATH" # if $XRAY_ENV_PATH was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
export XRAY_UTILS_DIR="$( cd -P "$( dirname "$XRAY_ENV_PATH" )" && pwd )"
export XRAY_DIR="$( dirname "$XRAY_UTILS_DIR" )"
export XRAY_DATABASE_DIR="${XRAY_DIR}/database"
export XRAY_TOOLS_DIR="${XRAY_DIR}/build/tools"
export XRAY_FUZZERS_DIR="${XRAY_DIR}/fuzzers"
export XRAY_FAMILY_DIR="${XRAY_DATABASE_DIR}/${XRAY_DATABASE}"

if [ -e "${XRAY_DIR}/env/bin/activate" ]; then
  source "${XRAY_DIR}/env/bin/activate"
fi

# misc
export XRAY_PART_YAML="${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/${XRAY_PART}/part.yaml"
source $XRAY_UTILS_DIR/environment.python.sh

# Set environment to default output and overwrite localisation settings
export LC_ALL=C

# tools
export XRAY_GENHEADER="${XRAY_UTILS_DIR}/genheader.sh"
export XRAY_BITREAD="${XRAY_TOOLS_DIR}/bitread --part_file ${XRAY_PART_YAML}"
export XRAY_MERGEDB="bash ${XRAY_UTILS_DIR}/mergedb.sh"
export XRAY_DBFIXUP="python3 ${XRAY_UTILS_DIR}/dbfixup.py"
export XRAY_MASKMERGE="bash ${XRAY_UTILS_DIR}/maskmerge.sh"
export XRAY_SEGMATCH="${XRAY_TOOLS_DIR}/segmatch"
export XRAY_SEGPRINT="python3 ${XRAY_UTILS_DIR}/segprint.py"
export XRAY_BIT2FASM="python3 ${XRAY_UTILS_DIR}/bit2fasm.py"
export XRAY_FASM2FRAMES="python3 ${XRAY_UTILS_DIR}/fasm2frames.py"
export XRAY_BITTOOL="${XRAY_TOOLS_DIR}/bittool"
export XRAY_BLOCKWIDTH="python3 ${XRAY_UTILS_DIR}/blockwidth.py"
export XRAY_PARSEDB="python3 ${XRAY_UTILS_DIR}/parsedb.py"
export XRAY_TCL_REFORMAT="${XRAY_UTILS_DIR}/tcl-reformat.sh"
export XRAY_VIVADO="${XRAY_UTILS_DIR}/vivado.sh"

# Verify an approved version is in use
export XRAY_VIVADO_SETTINGS="${XRAY_VIVADO_SETTINGS:-/opt/Xilinx/Vivado/2017.2/settings64.sh}"
# Vivado v2017.2 (64-bit)
if [ "$(${XRAY_VIVADO} -h |grep Vivado |cut -d\  -f 2)" != "v2017.2" ] ; then
    echo "Requires Vivado 2017.2. See https://github.com/SymbiFlow/prjxray/issues/14"
    # Can't exit since sourced script
    # Trash a key environment variable to preclude use
    export XRAY_DIR="/bad/vivado/version"
    return
fi
