XRAY_ENV_PATH="${BASH_SOURCE[0]}"
while [ -h "$XRAY_ENV_PATH" ]; do # resolve $XRAY_ENV_PATH until the file is no longer a symlink
  XRAY_UTILS_DIR="$( cd -P "$( dirname "$XRAY_ENV_PATH" )" && pwd )"
  XRAY_ENV_PATH="$(readlink "$XRAY_ENV_PATH")"
  [[ $XRAY_ENV_PATH != /* ]] && XRAY_ENV_PATH="$XRAY_UTILS_DIR/$XRAY_ENV_PATH" # if $XRAY_ENV_PATH was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
XRAY_UTILS_DIR="$( cd -P "$( dirname "$XRAY_ENV_PATH" )" && pwd )"

XRAY_DIR="$( dirname "$XRAY_UTILS_DIR" )"
XRAY_DATABASE_DIR="${XRAY_DIR}/database"
XRAY_TOOLS_DIR="${XRAY_DIR}/build/tools"

XRAY_GENHEADER="${XRAY_UTILS_DIR}/genheader.sh"
XRAY_BITREAD="${XRAY_TOOLS_DIR}/bitread"
XRAY_SEGMATCH="${XRAY_TOOLS_DIR}/segmatch"
XRAY_SEGPRINT="python2 ${XRAY_UTILS_DIR}/segprint.py"
