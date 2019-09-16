source $(dirname ${BASH_SOURCE[0]})/../utils/environment.sh
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
if [ $(${XRAY_VIVADO} -h |grep Vivado |cut -d\  -f 2) != "v2017.2" ] ; then
    echo "Requires Vivado 2017.2. See https://github.com/SymbiFlow/prjxray/issues/14"
    # Can't exit since sourced script
    # Trash a key environment variable to preclude use
    export XRAY_DIR="/bad/vivado/version"
    return
fi

