# dirs
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

if [ -e "${XRAY_DIR}/env/bin/activate" ]; then
  source "${XRAY_DIR}/env/bin/activate"
fi

# misc
export XRAY_PART_YAML="${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/${XRAY_PART}.yaml"
export PYTHONPATH="${XRAY_DIR}:${XRAY_DIR}/third_party/fasm:$PYTHONPATH"
